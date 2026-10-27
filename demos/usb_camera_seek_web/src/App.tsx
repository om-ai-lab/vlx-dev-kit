import { Activity, AlertCircle, Camera, Check, Crosshair, MessageSquareText, Pause, Play, RefreshCw, Signal, Square, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { connectCamera, createSession, getHealth, listCameras, sessionSocketUrl, type CameraDevice, type DetectionBox, type SessionEvent, type VideoSource } from "./api";

type Status = "idle" | "running" | "paused" | "stopped" | "error";
type Detection = { text: string; boxes: DetectionBox[]; targetClass: string; frameWidth: number; frameHeight: number; frameSequence: number; capturedAt: string; latencyMs: number };
const EMPTY_SOURCE: VideoSource = { id: "none", name: "未选择相机", kind: "none", status: "ready", createdAt: new Date().toISOString() };
const statusLabels: Record<Status, string> = { idle: "待开始", running: "检测中", paused: "已暂停", stopped: "已停止", error: "异常" };

export default function App() {
  const [cameras, setCameras] = useState<CameraDevice[]>([]);
  const [source, setSource] = useState<VideoSource>(EMPTY_SOURCE);
  const [targetClass, setTargetClass] = useState("人");
  const [status, setStatus] = useState<Status>("idle");
  const [detection, setDetection] = useState<Detection | null>(null);
  const [runtime, setRuntime] = useState<"checking" | "online" | "mock" | "offline">("checking");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<{ type: "info" | "error"; text: string } | null>(null);
  const [viewport, setViewport] = useState({ width: 0, height: 0 });
  const viewportRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const refresh = useCallback(async () => { try { setCameras(await listCameras()); } catch { setCameras([]); } }, []);
  useEffect(() => { void refresh(); void getHealth().then((h) => setRuntime(h.modelMock ? "mock" : "online")).catch(() => setRuntime("offline")); return () => socketRef.current?.close(); }, [refresh]);
  useEffect(() => { const element = viewportRef.current; if (!element) return; const update = () => setViewport({ width: element.clientWidth, height: element.clientHeight }); update(); const observer = new ResizeObserver(update); observer.observe(element); return () => observer.disconnect(); }, []);

  const connect = async (device: string) => {
    socketRef.current?.close(); setBusy(true); setDetection(null); setStatus("idle");
    try { setSource(await connectCamera(device)); setNotice({ type: "info", text: "USB 相机已连接" }); }
    catch (error) { setSource(EMPTY_SOURCE); setNotice({ type: "error", text: error instanceof Error ? error.message : "连接失败" }); }
    finally { setBusy(false); }
  };
  const onEvent = (event: SessionEvent) => {
    if (event.type === "state" && event.status) setStatus(event.status as Status);
    if (event.type === "detection_error") { setDetection(null); setNotice({ type: "error", text: event.detail || "Seek 检测失败" }); }
    if (event.type === "detection_result") {
      setDetection({ text: event.text || "未检测到目标", boxes: event.boxes || [], targetClass: event.targetClass || targetClass, frameWidth: Number(event.frameWidth), frameHeight: Number(event.frameHeight), frameSequence: Number(event.frameSequence), capturedAt: event.capturedAt || new Date().toISOString(), latencyMs: Number(event.latencyMs) });
      setNotice(null);
    }
  };
  const start = async () => {
    if (source.kind !== "camera" || !targetClass.trim()) return;
    socketRef.current?.close(); setStatus("running"); setDetection(null);
    try { const session = await createSession(source.id, targetClass.trim()); const socket = new WebSocket(sessionSocketUrl(session.id)); socketRef.current = socket; socket.onopen = () => socket.send(JSON.stringify({ type: "start" })); socket.onmessage = (message) => onEvent(JSON.parse(message.data) as SessionEvent); socket.onerror = () => { setStatus("error"); setNotice({ type: "error", text: "会话连接失败" }); }; }
    catch (error) { setStatus("error"); setNotice({ type: "error", text: error instanceof Error ? error.message : "启动失败" }); }
  };
  const command = (type: "pause" | "resume" | "stop") => socketRef.current?.send(JSON.stringify({ type }));
  const layout = useMemo(() => { if (!detection?.frameWidth || !detection.frameHeight) return null; const scale = Math.min(viewport.width / detection.frameWidth, viewport.height / detection.frameHeight); const width = detection.frameWidth * scale, height = detection.frameHeight * scale; return { left: (viewport.width - width) / 2, top: (viewport.height - height) / 2, width, height }; }, [detection, viewport]);

  return <div className="app-shell">
    <header className="topbar"><div className="brand-lockup"><div className="brand-mark"><Activity size={17} /></div><div className="brand-name">VLX<span>-</span>Seek</div></div><div className="current-workspace">单帧目标检测体验</div><div className="mode-switch"><span className="mode-option active"><Crosshair size={13} />Seek</span></div><div className={`connection-pill ${runtime === "offline" ? "is-offline" : "is-online"}`}><span className="status-dot" />{runtime === "online" ? "模型已连接" : runtime === "mock" ? "模拟模型" : runtime === "checking" ? "连接中" : "服务离线"}</div></header>
    <div className="workspace-grid">
      <aside className="source-rail"><div className="section-heading"><h2>USB 相机</h2><button className="icon-button" onClick={() => void refresh()} title="重新检测可用相机"><RefreshCw size={15} /></button></div><div className="source-content"><div className="camera-list">{cameras.length === 0 && <div className="source-empty"><Camera size={17} /><span>没有发现可用相机</span></div>}{cameras.map((camera) => <button key={camera.device} className={source.name === camera.name ? "camera-option active" : "camera-option"} disabled={!camera.available || busy} onClick={() => void connect(camera.device)}><Camera size={16} /><span><strong>{camera.name}</strong><small>{camera.device}</small></span><span className="device-status ready">可采集</span></button>)}</div></div><section className="seek-parameter-panel"><div className="parameter-title"><Crosshair size={14} />Seek 检测</div><label className="target-class-field"><span>目标类别</span><input value={targetClass} onChange={(event) => setTargetClass(event.target.value)} disabled={status === "running" || status === "paused"} placeholder="例如：人、车辆" /></label><div className="seek-parameter-note">单张图像、完整返回；每秒最多 1 次</div></section><div className="current-source"><Camera size={16} /><span><small>当前相机</small><strong>{source.name}</strong></span></div></aside>
      <main className="main-stage"><div className="stage-heading"><div><h1>Seek 目标检测</h1><span>USB 相机实时检测</span></div><span className={`task-status ${status}`}><span className="status-dot" />{statusLabels[status]}</span></div><section className="video-panel"><div ref={viewportRef} className="video-viewport">{source.playbackUrl ? <img className="camera-preview" src={source.playbackUrl} alt={source.name} /> : <div className="empty-video"><Camera size={34} /><strong>选择一个 USB 相机</strong><span>从左侧设备列表连接</span></div>}{detection && layout && <div className="detection-overlay"><div className="detection-content" style={layout}>{detection.boxes.map((box, index) => <div className="detection-box" key={`${detection.frameSequence}-${index}`} style={{ left: `${box.xmin / detection.frameWidth * 100}%`, top: `${box.ymin / detection.frameHeight * 100}%`, width: `${(box.xmax - box.xmin) / detection.frameWidth * 100}%`, height: `${(box.ymax - box.ymin) / detection.frameHeight * 100}%` }}><span className="detection-label">{box.label}</span></div>)}</div></div>}{source.kind === "camera" && <div className="viewport-status"><span><Signal size={12} />延迟预览</span></div>}</div></section><section className="conversation-panel"><div className="seek-live-summary"><span><Crosshair size={13} />目标：{targetClass || "未设置"}</span><span>{detection ? `${detection.boxes.length} 个目标 · ${detection.latencyMs} ms` : "等待检测结果"}</span></div><div className="task-actions"><button className="primary-button" onClick={() => void start()} disabled={source.kind !== "camera" || !targetClass.trim() || status === "running" || status === "paused"}><Play size={16} />开始检测</button><button className="secondary-button" onClick={() => command(status === "paused" ? "resume" : "pause")} disabled={status !== "running" && status !== "paused"}>{status === "paused" ? <Play size={15} /> : <Pause size={15} />}{status === "paused" ? "继续" : "暂停"}</button><button className="danger-button" onClick={() => command("stop")} disabled={status !== "running" && status !== "paused"}><Square size={14} />停止</button></div></section></main>
      <aside className="inspector-panel"><div className="section-heading"><div><h2>模型输出</h2><span>单次完整检测结果</span></div></div><div className="model-status"><span><Crosshair size={15} /><strong>VLX Seek</strong></span><span className={runtime}>{runtime === "online" ? "在线" : runtime === "mock" ? "模拟" : "离线"}</span></div><div className="message-list">{!detection ? <div className="empty-console"><MessageSquareText size={24} /><strong>等待模型输出</strong><span>选择相机并开始检测</span></div> : <div className="message-row assistant description"><div className="message-marker"><Crosshair size={12} /></div><div className="message-body"><div className="message-topline"><span>检测结果</span><time>{new Date(detection.capturedAt).toLocaleTimeString()}</time><span className="latency-label">延迟 {detection.latencyMs}ms</span></div><p>{detection.text}</p></div></div>}</div></aside>
    </div>
    {notice && <div className={`toast ${notice.type}`}><span>{notice.type === "error" ? <AlertCircle size={16} /> : <Check size={16} />}</span><span>{notice.text}</span><button onClick={() => setNotice(null)} title="关闭"><X size={15} /></button></div>}
  </div>;
}
