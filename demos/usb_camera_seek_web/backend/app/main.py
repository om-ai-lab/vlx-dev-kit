"""Minimal VLX-Seek demo runtime.

Only USB-camera capture, Seek inference, and the WebSocket session protocol are
kept here. Flow/video-upload/event-detection code is intentionally excluded.
"""
from __future__ import annotations

import asyncio
import base64
import math
import os
import re
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Protocol

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from omai_client import (
    VlxApiClient,
    VlxApiError,
    VlxSeekContent,
    VlxSeekImageUrl,
    VlxSeekMessage,
    VlxSeekRequest,
    VlxSeekResponse,
)
from pydantic import BaseModel
from requests import RequestException, Timeout

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

os.environ.setdefault("VLX_API_ENABLED", "true")
os.environ.setdefault("VLX_API_ENDPOINT", "http://172.16.37.118:8000/os/")
os.environ.setdefault("VLX_API_KEY", "YjI3YjM4OTQyZDczMjZkMWUzYTdAZVpHVWdxdzg=")
os.environ.setdefault("VLX_API_CONNECT_TIMEOUT_MS", "60000")
os.environ.setdefault("VLX_API_READ_TIMEOUT_MS", "60000")
os.environ.setdefault("VLX_API_WRITE_TIMEOUT_MS", "60000")

SEEK_MODEL = os.getenv("SEEK_MODEL", "vlx-seek-1.5-3b")
SEEK_ANALYSIS_FPS = max(0.1, float(os.getenv("SEEK_ANALYSIS_FPS", "1")))
SEEK_PREVIEW_DELAY_MS = max(0, int(os.getenv("SEEK_PREVIEW_DELAY_MS", "500")))
SEEK_MOCK = os.getenv("SEEK_MOCK", "0").lower() in {"1", "true", "yes"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CameraSnapshot:
    sequence: int
    jpeg: bytes | None
    width: int
    height: int
    captured_at: str | None
    error: str | None
    captured_monotonic: float = 0.0


class CameraHub:
    def __init__(self, device: str):
        self.device = device
        self.condition = threading.Condition()
        self.jpeg: bytes | None = None
        self.version = 0
        self.width = self.height = 0
        self.captured_at: str | None = None
        self.captured_monotonic = 0.0
        self.error: str | None = None
        self.history: list[CameraSnapshot] = []
        self.running = False
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True, name=f"seek-camera-{Path(self.device).name}")
        self.thread.start()

    def _run(self) -> None:
        if cv2 is None:
            self._set_error("OpenCV is not installed")
            return
        while self.running:
            capture = cv2.VideoCapture(self.device, cv2.CAP_V4L2)
            if not capture.isOpened():
                self._set_error(f"Unable to open {self.device}")
                time.sleep(1)
                continue
            try:
                while self.running:
                    ok, frame = capture.read()
                    if not ok:
                        self._set_error("Camera read failed")
                        break
                    ok, encoded = cv2.imencode(".jpg", frame)
                    if not ok:
                        self._set_error("Failed to encode camera frame")
                        break
                    jpeg = encoded.tobytes()
                    height, width = frame.shape[:2]
                    captured_at = now_iso()
                    captured_monotonic = time.monotonic()
                    with self.condition:
                        self.version += 1
                        self.jpeg, self.width, self.height = jpeg, int(width), int(height)
                        self.captured_at, self.captured_monotonic, self.error = captured_at, captured_monotonic, None
                        self.history.append(CameraSnapshot(self.version, jpeg, int(width), int(height), captured_at, None, captured_monotonic))
                        self.history = self.history[-900:]
                        self.condition.notify_all()
            finally:
                capture.release()

    def _set_error(self, detail: str) -> None:
        with self.condition:
            self.error = detail
            self.condition.notify_all()

    def _snapshot(self) -> CameraSnapshot:
        return CameraSnapshot(self.version, self.jpeg, self.width, self.height, self.captured_at, self.error, self.captured_monotonic)

    def wait_frame(self, last_version: int = -1, timeout: float = 5) -> CameraSnapshot:
        self.start()
        with self.condition:
            self.condition.wait_for(lambda: self.version > last_version or self.error is not None, timeout=timeout)
            return self._snapshot()

    def wait_delayed_frame(self, last_version: int = -1, delay_seconds: float = 0, timeout: float = 5) -> CameraSnapshot:
        self.start()
        deadline = time.monotonic() + timeout
        with self.condition:
            while True:
                cutoff = time.monotonic() - max(0, delay_seconds)
                for item in reversed(self.history):
                    if item.sequence > last_version and item.captured_monotonic <= cutoff:
                        return item
                if self.error or time.monotonic() >= deadline:
                    return self._snapshot()
                self.condition.wait(timeout=0.25)

    def wait_sampled_frame(self, last_version: int = -1, target_monotonic: float = 0, timeout: float = 5) -> CameraSnapshot:
        self.start()
        with self.condition:
            candidates = [item for item in self.history if item.sequence > last_version]
            if candidates:
                return next((item for item in candidates if item.captured_monotonic >= target_monotonic), candidates[-1])
            return self._snapshot()

    def stop(self) -> None:
        self.running = False
        with self.condition:
            self.condition.notify_all()


camera_hubs: dict[str, CameraHub] = {}
sources: dict[str, dict[str, Any]] = {}
sessions: dict[str, "SeekSession"] = {}


def get_camera_hub(device: str) -> CameraHub:
    hub = camera_hubs.setdefault(device, CameraHub(device))
    hub.start()
    return hub


@dataclass(frozen=True)
class SeekDetection:
    text: str
    boxes: list[dict[str, Any]]


def build_seek_prompt(target_class: str) -> str:
    target = target_class.strip()
    if not target:
        raise ValueError("Seek target class cannot be empty")
    return f"找到图中所有的：{target}。"


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _layers(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result, current, seen = [], payload, set()
    for _ in range(5):
        if not isinstance(current, dict) or id(current) in seen:
            break
        seen.add(id(current)); result.append(current)
        if isinstance(current.get("choices"), list):
            break
        current = next((current[k] for k in ("output", "response", "data", "result") if isinstance(current.get(k), dict)), None)
    return result


def _parse_boxes(raw_boxes: Any, target_class: str) -> list[dict[str, Any]]:
    if isinstance(raw_boxes, dict):
        raw_boxes = raw_boxes.get("preview", raw_boxes.get("boxes", []))
    boxes: list[dict[str, Any]] = []
    for item in raw_boxes if isinstance(raw_boxes, list) else []:
        if not isinstance(item, dict):
            continue
        values = [_number(item.get(key)) for key in ("xmin", "ymin", "xmax", "ymax")]
        if any(value is None for value in values) or values[2] <= values[0] or values[3] <= values[1]:
            continue
        boxes.append({"xmin": max(0, values[0]), "ymin": max(0, values[1]), "xmax": max(0, values[2]), "ymax": max(0, values[3]), "label": str(item.get("label", target_class))})
    return boxes


def parse_seek_response(payload: Any, target_class: str = "") -> SeekDetection:
    if not isinstance(payload, dict):
        raise ValueError("Seek response is not a JSON object")
    layers = _layers(payload)
    for layer in layers:
        code = _number(layer.get("code"))
        if code is not None and code >= 400:
            raise ValueError(f"Seek 服务内部错误 code={int(code)}")
    body = next((item for item in layers if isinstance(item.get("choices"), list)), payload)
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ValueError("Seek response has no choices")
    choice = choices[0]; message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
    text = message.get("content") or choice.get("content") or ""
    if not isinstance(text, str):
        text = str(text)
    raw_boxes = choice.get("result_bbox_list", message.get("result_bbox_list", body.get("result_bbox_list", [])))
    return SeekDetection(text.strip(), _parse_boxes(raw_boxes, target_class))


def parse_seek_sdk_response(response: VlxSeekResponse, target_class: str = "") -> SeekDetection:
    code = _number(response.raw.get("code"))
    if code is not None and code >= 400:
        raise ValueError(f"Seek 服务内部错误 code={int(code)}")
    if not response.choices:
        raise ValueError("Seek response has no choices")
    choice = response.choices[0]
    text = choice.message.content if choice.message and choice.message.content else ""
    return SeekDetection(text.strip(), _parse_boxes(choice.result_bbox_list, target_class))


class SeekSdkClient(Protocol):
    def vlx_seek(self, request: VlxSeekRequest) -> VlxSeekResponse:
        ...


class SeekGateway:
    def __init__(self, client: SeekSdkClient | None = None):
        self._client = client

    @staticmethod
    def build_request(image: bytes, prompt: str) -> VlxSeekRequest:
        encoded = base64.b64encode(image).decode()
        image_content = VlxSeekContent(
            type="image_url",
            image_url=VlxSeekImageUrl(url=f"data:image/jpeg;base64,{encoded}"),
        )
        text_content = VlxSeekContent(type="text", text=prompt)
        message = VlxSeekMessage(role="user", content=[image_content, text_content])
        return VlxSeekRequest(
            model=SEEK_MODEL,
            messages=[message],
            bbox_list=None,
            max_tokens=4096,
            temperature=0.0,
            top_p=1.0,
        )

    def _get_client(self) -> SeekSdkClient:
        if self._client is None:
            self._client = VlxApiClient.from_env()
        return self._client

    async def detect(self, image: bytes, prompt: str, target_class: str) -> SeekDetection:
        if SEEK_MOCK:
            return SeekDetection(f"Mock Seek detection: {target_class}", [])
        try:
            request = self.build_request(image, prompt)
            response = await asyncio.to_thread(self._get_client().vlx_seek, request)
            return parse_seek_sdk_response(response, target_class)
        except Timeout as error:
            raise RuntimeError("Seek 请求超时") from error
        except (VlxApiError, RequestException) as error:
            raise RuntimeError(f"Seek service request failed: {error}") from error
        except (ValueError, TypeError) as error:
            raise RuntimeError(f"Invalid Seek response: {error}") from error


seek_gateway = SeekGateway()


class SeekSession:
    def __init__(self, session_id: str, source_id: str, target_class: str):
        self.id, self.source_id, self.target_class = session_id, source_id, target_class
        self.status = "idle"
        self.clients: set[WebSocket] = set()
        self.task: asyncio.Task[None] | None = None

    async def emit(self, event: dict[str, Any]) -> None:
        for client in list(self.clients):
            try:
                await client.send_json(event)
            except Exception:
                self.clients.discard(client)

    async def run(self) -> None:
        device = str(sources[self.source_id]["file_name"]); hub = get_camera_hub(device)
        sequence = -1; interval = 1 / SEEK_ANALYSIS_FPS
        while self.status in {"running", "paused"}:
            if self.status == "paused":
                await asyncio.sleep(0.1); continue
            started = time.perf_counter(); snap = await asyncio.to_thread(hub.wait_frame, sequence, max(1, interval * 2))
            if snap.sequence <= sequence or snap.jpeg is None:
                await asyncio.sleep(0.1); continue
            sequence = snap.sequence; request_id = str(uuid.uuid4()); request_started = time.perf_counter()
            try:
                result = await seek_gateway.detect(snap.jpeg, build_seek_prompt(self.target_class), self.target_class)
                await self.emit({"type": "detection_result", "requestId": request_id, "targetClass": self.target_class, "text": result.text or "No target detected", "boxes": result.boxes, "frameWidth": snap.width, "frameHeight": snap.height, "frameSequence": snap.sequence, "capturedAt": snap.captured_at, "latencyMs": round((time.perf_counter() - request_started) * 1000), "previewDelayMs": SEEK_PREVIEW_DELAY_MS})
            except Exception as error:
                await self.emit({"type": "detection_error", "requestId": request_id, "targetClass": self.target_class, "frameSequence": snap.sequence, "detail": str(error)})
            await asyncio.sleep(max(0, interval - (time.perf_counter() - started)))

    async def start(self) -> None:
        if self.status != "running":
            self.status = "running"; self.task = asyncio.create_task(self.run())

    async def stop(self) -> None:
        self.status = "stopped"
        if self.task and not self.task.done():
            self.task.cancel()


class CameraCreate(BaseModel):
    device: str


class SessionCreate(BaseModel):
    model: str = "seek"
    sourceId: str
    targetClass: str | None = None


app = FastAPI(title="VLX-Seek Local Runtime", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {"ok": True, "model": "VLX Seek", "modelMock": SEEK_MOCK, "opencv": cv2 is not None, "seekPreviewDelayMs": SEEK_PREVIEW_DELAY_MS}


@app.get("/api/cameras")
async def list_cameras() -> list[dict[str, Any]]:
    result = []
    for device in sorted(Path("/dev").glob("video*")):
        if re.fullmatch(r"video\d+", device.name):
            result.append({"device": str(device), "name": f"USB Camera {device.name.removeprefix('video')}", "available": os.access(device, os.R_OK | os.W_OK)})
    return result


@app.post("/api/sources/camera")
async def create_camera(payload: CameraCreate) -> dict[str, Any]:
    device = payload.device.strip()
    if not re.fullmatch(r"/dev/video\d+", device) or not Path(device).exists():
        raise HTTPException(404, "USB camera does not exist")
    source_id = "camera-" + Path(device).name
    sources[source_id] = {"id": source_id, "name": "USB Camera " + Path(device).name.removeprefix("video"), "kind": "camera", "status": "ready", "file_name": device, "playbackUrl": f"/api/cameras/{source_id}/stream", "createdAt": now_iso()}
    get_camera_hub(device)
    return sources[source_id]


@app.get("/api/sources")
async def list_sources() -> list[dict[str, Any]]:
    return list(sources.values())


@app.get("/api/sources/{source_id}")
async def get_source(source_id: str) -> dict[str, Any]:
    source = sources.get(source_id)
    if not source:
        raise HTTPException(404, "Camera source not found")
    return source


@app.get("/api/cameras/{source_id}/stream")
async def camera_stream(source_id: str) -> StreamingResponse:
    source = sources.get(source_id)
    if not source:
        raise HTTPException(404, "Camera source not found")
    hub = get_camera_hub(str(source["file_name"]))
    async def frames() -> AsyncIterator[bytes]:
        version = -1
        while True:
            snap = await asyncio.to_thread(hub.wait_delayed_frame, version, SEEK_PREVIEW_DELAY_MS / 1000, 5)
            if snap.jpeg is None or snap.sequence <= version:
                continue
            version = snap.sequence
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + snap.jpeg + b"\r\n"
    return StreamingResponse(frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.post("/api/sessions")
async def create_session(payload: SessionCreate) -> dict[str, Any]:
    target = (payload.targetClass or "").strip()
    if not target:
        raise HTTPException(422, "Seek target class cannot be empty")
    source = sources.get(payload.sourceId)
    if not source or source["kind"] != "camera":
        raise HTTPException(422, "Seek requires a USB camera source")
    session_id = str(uuid.uuid4()); session = SeekSession(session_id, payload.sourceId, target); sessions[session_id] = session
    return {"id": session_id, "sourceId": payload.sourceId, "sourceName": source["name"], "instruction": build_seek_prompt(target), "status": "idle", "model": "seek", "targetClass": target, "createdAt": now_iso(), "updatedAt": now_iso()}


@app.websocket("/api/sessions/{session_id}/events")
async def session_events(websocket: WebSocket, session_id: str) -> None:
    session = sessions.get(session_id)
    if not session:
        await websocket.close(code=4404); return
    await websocket.accept(); session.clients.add(websocket)
    await websocket.send_json({"type": "state", "sessionId": session_id, "status": session.status})
    try:
        while True:
            message = await websocket.receive_json(); kind = message.get("type")
            if kind == "start": await session.start()
            elif kind == "pause": session.status = "paused"
            elif kind == "resume": await session.start()
            elif kind == "stop": await session.stop()
            await session.emit({"type": "state", "sessionId": session_id, "status": session.status})
    except WebSocketDisconnect:
        session.clients.discard(websocket)
