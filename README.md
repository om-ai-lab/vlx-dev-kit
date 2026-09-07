<p align="center">
  <h1 align="center">VLX Development Kit</h1>
</p>

<p align="center">Edge AI development resources for the VLX Development Module and VLX-Seek.</p>

<p align="center">English | <a href="README_ZH.md">中文</a></p>

This repository collects the developer documentation and runnable web demo for the VLX Development Module. The current demo focuses on **VLX-Seek**: it captures frames from a USB camera, sends them to a Seek inference service, and displays detected targets and bounding boxes in a browser.

## Contents

| Path | Description |
| --- | --- |
| [`docs/en/`](docs/en/) | English developer documentation |
| [`docs/zh/`](docs/zh/) | Chinese developer documentation |
| [`demos/usb_camera_seek_web/`](demos/usb_camera_seek_web/) | VLX-Seek USB-camera web demo |

### Developer documentation directory

The documentation follows the complete development-module workflow, from hardware setup and operating-system installation to model API integration and troubleshooting. `docs/en/` and `docs/zh/` have the same chapter structure and numbering, making it easy to switch languages while staying on the same topic.

```text
docs/
├── en/                                      # English documentation
│   ├── 0 VLX Development Module Product Introduction/
│   ├── 1 Quick Start/
│   ├── 2 System Installation and Configuration/
│   ├── 3 Algorithm Application Development/
│   │   ├── 3.1 Model Development APIs/
│   │   └── 3.2 SDK Integration Guide/
│   └── 4 FAQ/
└── zh/                                      # Chinese documentation, same layout
```

#### 0. VLX Development Module Product Introduction

| Document | What it covers |
| --- | --- |
| [Product Introduction](<docs/en/0 VLX Development Module Product Introduction/Product Introduction.md>) | Product positioning, core capabilities, typical use cases, and a reading guide for the documentation set |
| [Package Contents](<docs/en/0 VLX Development Module Product Introduction/Package Contents.md>) | Hardware, accessories, and other items included with the development module |
| [Common Terms](<docs/en/0 VLX Development Module Product Introduction/Common Terms.md>) | Frequently used hardware, system, model, and deployment terminology |

#### 1. Quick Start

| Document | What it covers |
| --- | --- |
| [1.1 Hardware Overview](<docs/en/1 Quick Start/1.1 Hardware Overview.md>) | Module specifications, connectors, indicators, buttons, and I/O interfaces |
| [1.2 System Flashing](<docs/en/1 Quick Start/1.2 System Flashing.md>) | Prerequisites and steps for flashing the supplied system image |
| [1.3 First Boot and Quick Acceptance](<docs/en/1 Quick Start/1.3 First Boot and Quick Acceptance.md>) | Initial startup, login, and basic hardware and service verification |
| [1.4 System Recovery](<docs/en/1 Quick Start/1.4 System Recovery.md>) | Restoring the device when the system cannot boot or operate normally |
| [1.5 Backup and Diagnostics](<docs/en/1 Quick Start/1.5 Backup and Diagnostics.md>) | Backing up important data and collecting diagnostic information |
| [1.6 Obtaining the SN](<docs/en/1 Quick Start/1.6 Obtaining the SN.md>) | Locating and reading the device serial number |
| [1.7 License Management](<docs/en/1 Quick Start/1.7 License Management.md>) | Checking, importing, and maintaining model or device licenses |

#### 2. System Installation and Configuration

| Document | What it covers |
| --- | --- |
| [2.1 Create a System Disk](<docs/en/2 System Installation and Configuration/2.1 Create System Disk.md>) | Preparing installation media from a system image |
| [2.2 Install the System](<docs/en/2 System Installation and Configuration/2.2 Install System.md>) | Installing and initializing the operating system on the module |
| [2.3 Network Configuration](<docs/en/2 System Installation and Configuration/2.3 Network Configuration.md>) | Ethernet, DHCP, static IP, Wi-Fi, connectivity tests, and common diagnostics |
| [2.4 Install Algorithm Programs](<docs/en/2 System Installation and Configuration/2.4 Install Algorithm Programs.md>) | Deploying model packages and their runtime dependencies |
| [2.5 Configure Auto-start](<docs/en/2 System Installation and Configuration/2.5 Configure Auto-start.md>) | Starting algorithm applications and related services automatically at boot |
| [2.6 Restart Algorithm Service](<docs/en/2 System Installation and Configuration/2.6 Restart Algorithm Service.md>) | Checking service status and safely restarting algorithm services |
| [2.7 System Upgrade](<docs/en/2 System Installation and Configuration/2.7 System Upgrade.md>) | Upgrade preparation, execution, verification, and rollback considerations |

#### 3. Algorithm Application Development

| Directory or document | What it covers |
| --- | --- |
| `3.1 Model Development APIs/` | Model-specific HTTP APIs, request and response schemas, multimodal input, authentication, and examples |
| [3.1.1 VLX-Flow](<docs/en/3 Algorithm Application Development/3.1 Model Development APIs/3.1.1 VLX-Flow.md>) | VLX-Flow model invocation and parameters |
| [3.1.2 VLX-Seek](<docs/en/3 Algorithm Application Development/3.1 Model Development APIs/3.1.2 VLX-Seek.md>) | Open-vocabulary target search, image input, text results, and bounding boxes |
| [3.1.3 OmDet-Turbo](<docs/en/3 Algorithm Application Development/3.1 Model Development APIs/3.1.3 OmDet-Turbo.md>) | OmDet-Turbo detection API usage |
| [3.1.4 Multimodal Model-OmChat](<docs/en/3 Algorithm Application Development/3.1 Model Development APIs/3.1.4 Multimodal Model-OmChat.md>) | OmChat multimodal conversation API usage |
| `3.2 SDK Integration Guide/` | Language SDK setup, client initialization, calls, result handling, and error handling |
| [3.2.1 Java SDK](<docs/en/3 Algorithm Application Development/3.2 SDK Integration Guide/3.2.1 Java SDK.md>) | Integrating VLX model services into Java applications |
| [3.2.2 Python SDK](<docs/en/3 Algorithm Application Development/3.2 SDK Integration Guide/3.2.2 Python SDK.md>) | Integrating VLX model services into Python applications |

#### 4. FAQ

| Document | What it covers |
| --- | --- |
| [Q&A](<docs/en/4 FAQ/Q&A.md>) | Troubleshooting model startup, licenses, upgrades, storage, remote access, and diagnostic exports |

## Application demos

The `demos/` directory contains runnable application examples built around VLX-series models. Each demo is kept in its own subdirectory and can include its frontend, backend, deployment configuration, and usage guide. These examples are intended for validating model APIs, learning the integration flow, and adapting VLX models to edge-device scenarios.

At present, the repository includes only one demo:

- **`usb_camera_seek_web`** — a full-stack VLX-Seek example. The browser UI selects a USB camera and target class; the Python backend captures frames, calls the Seek endpoint, and returns detection text and bounding boxes over WebSocket. It can run locally or through Docker and supports a mock mode when no model service is available.

```text
demos/
└── usb_camera_seek_web/
    ├── src/                 # React and TypeScript frontend
    ├── backend/             # FastAPI backend, camera capture, and Seek client
    ├── docker-compose.yml   # Full-stack container orchestration
    ├── Dockerfile.web       # Frontend production image
    ├── nginx.conf           # Static hosting and backend proxy configuration
    ├── package.json         # Frontend dependencies and scripts
    └── README.md            # Demo-specific setup and usage guide
```

### `usb_camera_seek_web`: VLX-Seek Studio

#### Features

- Discover and connect to a USB camera.
- Submit one camera frame per analysis cycle to VLX-Seek.
- Enter an open-vocabulary target such as `person`, `vehicle`, or `red helmet`.
- Render model text and bounding boxes in real time.
- Pause, resume, and stop a detection session.
- Run with a real Seek service or with `SEEK_MOCK=1` for UI testing.

#### Requirements

- Node.js 18 or later and npm
- Python 3.10 or later
- A Linux host with an accessible `/dev/video*` USB camera for real capture
- A VLX-Seek-compatible HTTP endpoint (OpenAI-compatible chat completions API)

#### Run locally

Start the backend in one terminal:

```bash
cd demos/usb_camera_seek_web/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Start the frontend in another terminal:

```bash
cd demos/usb_camera_seek_web
npm install
npm run dev
```

Open <http://localhost:5173> in a browser. The Vite development server proxies `/api` requests according to the project configuration.

To run without a model service:

```bash
SEEK_MOCK=1 uvicorn app.main:app --reload --port 8000
```

#### Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `VLX_API_ENABLED` | `true` | Enable the VLX SDK client |
| `VLX_API_ENDPOINT` | `http://172.16.37.118:8000/os/` | VLX API gateway endpoint used by the SDK |
| `VLX_API_KEY` | Value from `demo.py` | VLX API access key used for bearer authentication |
| `VLX_API_CONNECT_TIMEOUT_MS` | `60000` | SDK connection timeout in milliseconds |
| `VLX_API_READ_TIMEOUT_MS` | `60000` | SDK response timeout in milliseconds |
| `VLX_API_WRITE_TIMEOUT_MS` | `60000` | SDK write timeout in milliseconds |
| `SEEK_MODEL` | `vlx-seek-1.5-3b` | Model ID sent in requests |
| `SEEK_ANALYSIS_FPS` | `1` | Maximum analysis cycles per second |
| `SEEK_PREVIEW_DELAY_MS` | `500` | Camera preview delay in milliseconds |
| `SEEK_MOCK` | `0` | Return mock detections when set to `1`, `true`, or `yes` |

For Docker deployment:

```bash
cd demos/usb_camera_seek_web
docker compose up --build
```

The web UI is exposed at <http://127.0.0.1:5173>. The Compose file maps `/dev/video0` by default; set `VIDEO_DEVICE` to use another camera device.

## Seek SDK integration

The backend uses the `omai==1.0.3` Python SDK. It creates a client with `VlxApiClient.from_env()`, builds the multimodal request with the SDK's typed request classes, and calls `vlx_api_client.vlx_seek(request)` in a worker thread. The response exposes detection text through `choices[].message.content` and boxes through `choices[].result_bbox_list`.

## Documentation

- [English documentation](docs/en/)
- [中文文档](docs/zh/)
- [VLX-Seek API guide](<docs/en/3 Algorithm Application Development/3.1 Model Development APIs/3.1.2 VLX-Seek.md>)
- [VLX-Seek Studio guide](demos/usb_camera_seek_web/README.md)

## Development checks

Backend tests:

```bash
PYTHONPATH=demos/usb_camera_seek_web/backend \
  python -m unittest discover -s demos/usb_camera_seek_web/backend/tests
```

Frontend production build:

```bash
cd demos/usb_camera_seek_web
npm install
npm run build
```

## License and support

Check the accompanying documentation and model distribution terms before deploying the kit in production. For product, integration, or technical support, contact the VLX project team through your organization’s support channel.
