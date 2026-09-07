export type CameraDevice = { device: string; name: string; available: boolean };
export type VideoSource = { id: string; name: string; kind: "camera" | "none"; status: "ready" | "offline"; playbackUrl?: string; createdAt: string };
export type DetectionBox = { xmin: number; ymin: number; xmax: number; ymax: number; label: string };
export type SessionEvent = { type: string; status?: string; detail?: string; text?: string; requestId?: string; targetClass?: string; boxes?: DetectionBox[]; frameWidth?: number; frameHeight?: number; frameSequence?: number; capturedAt?: string; latencyMs?: number; previewDelayMs?: number };

async function json<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

export const getHealth = async () => json<{ modelMock: boolean; seekPreviewDelayMs: number }>(await fetch("/api/health"));
export const listCameras = async () => json<CameraDevice[]>(await fetch("/api/cameras"));
export const connectCamera = async (device: string) => json<VideoSource>(await fetch("/api/sources/camera", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ device }) }));
export const createSession = async (sourceId: string, targetClass: string) => json<{ id: string }>(await fetch("/api/sessions", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ model: "seek", sourceId, targetClass }) }));
export function sessionSocketUrl(sessionId: string): string {
  return `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/api/sessions/${sessionId}/events`;
}
