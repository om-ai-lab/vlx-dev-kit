from __future__ import annotations

import asyncio
import base64
import time
import unittest
from unittest.mock import patch

from requests import ReadTimeout

from app import main


class FakeSeekClient:
    requests: list[main.VlxSeekRequest] = []
    response_payload: dict[str, object] = {
        "choices": [{
            "message": {"content": "发现目标"},
            "result_bbox_list": [{
                "xmin": 12,
                "ymin": 18,
                "xmax": 120,
                "ymax": 180,
                "label": "人",
            }],
        }],
    }
    error: Exception | None = None

    def vlx_seek(self, request: main.VlxSeekRequest) -> main.VlxSeekResponse:
        self.requests.append(request)
        if self.error:
            raise self.error
        return main.VlxSeekResponse.from_dict(self.response_payload)


class SeekAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        FakeSeekClient.requests = []
        FakeSeekClient.error = None
        FakeSeekClient.response_payload = {
            "choices": [{
                "message": {"content": "发现目标"},
                "result_bbox_list": [{
                    "xmin": 12,
                    "ymin": 18,
                    "xmax": 120,
                    "ymax": 180,
                    "label": "人",
                }],
            }],
        }

    def test_sdk_request_contains_one_image_and_expected_model(self) -> None:
        request = main.SeekGateway.build_request(b"jpeg-bytes", "识别每个：人")
        content = request.messages[0].content

        self.assertEqual(request.model, "vlx-seek-1.5-3b")
        self.assertIsNone(request.bbox_list)
        self.assertEqual(request.max_tokens, 4096)
        self.assertEqual(request.temperature, 0.0)
        self.assertEqual(request.top_p, 1.0)
        self.assertEqual(
            [item.type for item in content],
            ["image_url", "text"],
        )
        image_url = content[0].image_url.url
        self.assertEqual(
            image_url,
            "data:image/jpeg;base64," + base64.b64encode(b"jpeg-bytes").decode(),
        )

    def test_response_parser_maps_bbox_and_discards_invalid_box(self) -> None:
        result = main.parse_seek_response({
            "choices": [{
                "message": {"content": "发现目标"},
                "result_bbox_list": [
                    {"xmin": "12", "ymin": 18, "xmax": 120, "ymax": 180, "label": "人"},
                    {"xmin": 30, "ymin": 30, "xmax": 20, "ymax": 50},
                ],
            }],
        }, "人")

        self.assertEqual(result.text, "发现目标")
        self.assertEqual(result.boxes, [{
            "xmin": 12.0,
            "ymin": 18.0,
            "xmax": 120.0,
            "ymax": 180.0,
            "label": "人",
        }])

    def test_response_parser_unwraps_seek_event_and_bbox_preview(self) -> None:
        result = main.parse_seek_response({
            "event": "response",
            "request_id": "seek-request",
            "output": {
                "code": 200,
                "choices": [{
                    "message": {"content": "<ground>人</ground><objects>None</objects>"},
                    "result_bbox_list": {
                        "count": 1,
                        "preview": [{
                            "xmin": 20,
                            "ymin": 30,
                            "xmax": 220,
                            "ymax": 330,
                            "label": "人",
                        }],
                        "truncated": 0,
                    },
                }],
            },
        }, "人")

        self.assertEqual(result.text, "<ground>人</ground><objects>None</objects>")
        self.assertEqual(result.boxes, [{
            "xmin": 20.0,
            "ymin": 30.0,
            "xmax": 220.0,
            "ymax": 330.0,
            "label": "人",
        }])

    def test_empty_target_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            main.build_seek_prompt("  ")

    def test_prompt_matches_sdk_demo(self) -> None:
        self.assertEqual(main.build_seek_prompt(" 火 "), "找到图中所有的：火。")

    def test_gateway_creates_sdk_client_from_environment(self) -> None:
        client = FakeSeekClient()
        with patch.object(main, "SEEK_MOCK", False):
            with patch.object(main.VlxApiClient, "from_env", return_value=client) as from_env:
                asyncio.run(main.SeekGateway().detect(b"image", "找到图中所有的：人。", "人"))

        from_env.assert_called_once_with()
        self.assertEqual(len(FakeSeekClient.requests), 1)

    def test_detect_returns_complete_json_and_maps_service_errors(self) -> None:
        client = FakeSeekClient()
        with patch.object(main, "SEEK_MOCK", False):
            result = asyncio.run(main.SeekGateway(client).detect(b"image", "识别每个：人", "人"))

        self.assertEqual(result.text, "发现目标")
        self.assertEqual(len(result.boxes), 1)
        self.assertEqual(len(FakeSeekClient.requests), 1)
        request = FakeSeekClient.requests[0]
        self.assertEqual(request.model, "vlx-seek-1.5-3b")
        self.assertEqual(len(request.messages[0].content), 2)

        FakeSeekClient.error = ReadTimeout("timeout")
        with patch.object(main, "SEEK_MOCK", False):
            with self.assertRaisesRegex(RuntimeError, "超时"):
                asyncio.run(main.SeekGateway(client).detect(b"image", "识别每个：人", "人"))

    def test_detect_wraps_http_200_business_error(self) -> None:
        FakeSeekClient.response_payload = {
            "code": 500,
            "took": 34,
            "answer": None,
            "error": None,
        }
        client = FakeSeekClient()
        with patch.object(main, "SEEK_MOCK", False):
            with self.assertRaisesRegex(RuntimeError, r"Seek 服务内部错误 code=500"):
                asyncio.run(main.SeekGateway(client).detect(b"image", "识别每个：人", "人"))


    def test_delayed_frame_selects_latest_frame_before_cutoff(self) -> None:
        hub = main.CameraHub("/dev/video-test")
        hub.start = lambda: None  # type: ignore[method-assign]
        now = time.monotonic()
        hub.history.extend([
            main.CameraSnapshot(
                sequence=1,
                jpeg=b"frame-1",
                width=640,
                height=480,
                captured_at=None,
                error=None,
                captured_monotonic=now - 3.0,
            ),
            main.CameraSnapshot(
                sequence=2,
                jpeg=b"frame-2",
                width=640,
                height=480,
                captured_at=None,
                error=None,
                captured_monotonic=now - 2.0,
            ),
            main.CameraSnapshot(
                sequence=3,
                jpeg=b"frame-3",
                width=640,
                height=480,
                captured_at=None,
                error=None,
                captured_monotonic=now - 1.0,
            ),
        ])
        result = hub.wait_delayed_frame(last_version=0, delay_seconds=1.5, timeout=0)
        self.assertEqual(result.sequence, 2)

    def test_sampled_frame_selects_first_buffered_frame_after_target(self) -> None:
        hub = main.CameraHub("/dev/video-test")
        hub.start = lambda: None  # type: ignore[method-assign]
        now = time.monotonic()
        hub.history.extend([
            main.CameraSnapshot(
                sequence=1,
                jpeg=b"frame-1",
                width=640,
                height=480,
                captured_at=None,
                error=None,
                captured_monotonic=now - 3.0,
            ),
            main.CameraSnapshot(
                sequence=2,
                jpeg=b"frame-2",
                width=640,
                height=480,
                captured_at=None,
                error=None,
                captured_monotonic=now - 1.0,
            ),
        ])
        result = hub.wait_sampled_frame(
            last_version=0,
            target_monotonic=now - 1.5,
            timeout=0,
        )
        self.assertEqual(result.sequence, 2)

if __name__ == "__main__":

    unittest.main()
