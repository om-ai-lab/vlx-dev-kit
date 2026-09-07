<p align="center">
  <h1 align="center">VLX 开发套件</h1>
</p>

<p align="center">VLX 开发模组的边缘 AI 开发资源。</p>

<p align="center"><a href="README.md">English</a> | 中文</p>

本仓库包含 VLX 开发模组的开发者文档和可运行 Web Demo。当前 Demo 聚焦 **VLX-Seek**：从 USB 摄像头采集图像帧，调用 Seek 推理服务，并在浏览器中实时显示目标和边界框。

## 目录结构

| 路径 | 说明 |
| --- | --- |
| [`docs/en/`](docs/en/) | 英文开发文档 |
| [`docs/zh/`](docs/zh/) | 中文开发文档 |
| [`demos/usb_camera_seek_web/`](demos/usb_camera_seek_web/) | VLX-Seek USB 摄像头 Web Demo |

### 开发文档目录

开发文档按照开发模组的完整使用流程组织，从硬件认识、系统安装与配置，一直到模型接口集成和问题排查。`docs/zh/` 与 `docs/en/` 使用相同的章节结构和编号，方便在中英文版本之间定位同一主题。

```text
docs/
├── zh/                              # 中文开发文档
│   ├── 0 VLX开发模组产品介绍/
│   ├── 1 快速开始/
│   ├── 2 系统安装与配置/
│   ├── 3 算法应用开发/
│   │   ├── 3.1 模型开发接口/
│   │   └── 3.2 SDK调用指南/
│   └── 4 常见问题/
└── en/                              # 英文开发文档，目录结构与中文版一致
```

#### 0. VLX 开发模组产品介绍

| 文档 | 内容说明 |
| --- | --- |
| [产品介绍](<docs/zh/0 VLX开发模组产品介绍/产品介绍.md>) | 产品定位、核心能力、典型用途及整套开发文档的阅读指引 |
| [包装清单](<docs/zh/0 VLX开发模组产品介绍/包装清单.md>) | 开发模组、配件及随附物品说明 |
| [常见术语](<docs/zh/0 VLX开发模组产品介绍/常见术语.md>) | 文档中常用的硬件、系统、模型和部署术语 |

#### 1. 快速开始

| 文档 | 内容说明 |
| --- | --- |
| [1.1 硬件简介](<docs/zh/1 快速开始/1.1 硬件简介.md>) | 模组规格、连接器、指示灯、按键和 I/O 接口 |
| [1.2 系统烧录](<docs/zh/1 快速开始/1.2 系统烧录.md>) | 系统镜像烧录前的准备工作和操作步骤 |
| [1.3 首次启动与快速验收](<docs/zh/1 快速开始/1.3 首次启动与快速验收.md>) | 首次开机、登录及硬件和服务的基础检查 |
| [1.4 系统恢复](<docs/zh/1 快速开始/1.4 系统恢复.md>) | 系统无法正常启动或运行时的恢复方法 |
| [1.5 备份与诊断](<docs/zh/1 快速开始/1.5 备份与诊断.md>) | 重要数据备份及诊断信息收集 |
| [1.6 SN 码获取](<docs/zh/1 快速开始/1.6 SN码获取.md>) | 查找和读取设备序列号 |
| [1.7 授权管理](<docs/zh/1 快速开始/1.7 授权管理.md>) | 查看、导入和维护模型或设备授权 |

#### 2. 系统安装与配置

| 文档 | 内容说明 |
| --- | --- |
| [2.1 制作系统盘](<docs/zh/2 系统安装与配置/2.1 制作系统盘.md>) | 使用系统镜像制作安装介质 |
| [2.2 安装系统](<docs/zh/2 系统安装与配置/2.2 安装系统.md>) | 在开发模组上安装和初始化操作系统 |
| [2.3 网络配置](<docs/zh/2 系统安装与配置/2.3 网络配置.md>) | 有线网络、DHCP、静态 IP、Wi-Fi、连通性测试和常见排查 |
| [2.4 安装算法程序](<docs/zh/2 系统安装与配置/2.4 安装算法程序.md>) | 部署模型程序包及其运行环境 |
| [2.5 开机自启动配置](<docs/zh/2 系统安装与配置/2.5 开机自启动配置.md>) | 配置算法应用和相关服务随系统自动启动 |
| [2.6 算法服务重启](<docs/zh/2 系统安装与配置/2.6 算法服务重启.md>) | 查看服务状态并安全重启算法服务 |
| [2.7 系统升级](<docs/zh/2 系统安装与配置/2.7 系统升级.md>) | 升级前准备、升级操作、结果验证和回退注意事项 |

#### 3. 算法应用开发

| 目录或文档 | 内容说明 |
| --- | --- |
| `3.1 模型开发接口/` | 各模型的 HTTP 接口、请求与响应结构、鉴权、多模态输入和调用示例 |
| [3.1.1 VLX-Flow](<docs/zh/3 算法应用开发/3.1 模型开发接口/3.1.1 VLX-Flow.md>) | VLX-Flow 模型调用方式和参数说明 |
| [3.1.2 VLX-Seek](<docs/zh/3 算法应用开发/3.1 模型开发接口/3.1.2 VLX-Seek.md>) | 开放词表目标搜索、图像输入、文本结果和边界框 |
| [3.1.3 OmDet-Turbo](<docs/zh/3 算法应用开发/3.1 模型开发接口/3.1.3 OmDet-Turbo.md>) | OmDet-Turbo 检测接口的使用方法 |
| [3.1.4 多模态模型 OmChat](<docs/zh/3 算法应用开发/3.1 模型开发接口/3.1.4 多模态模型-OmChat.md>) | OmChat 多模态对话接口的使用方法 |
| `3.2 SDK调用指南/` | SDK 安装、客户端初始化、接口调用、结果处理和异常处理 |
| [3.2.1 Java SDK](<docs/zh/3 算法应用开发/3.2 SDK调用指南/3.2.1 Java SDK.md>) | 在 Java 应用中集成 VLX 模型服务 |
| [3.2.2 Python SDK](<docs/zh/3 算法应用开发/3.2 SDK调用指南/3.2.2 Python SDK.md>) | 在 Python 应用中集成 VLX 模型服务 |

#### 4. 常见问题

| 文档 | 内容说明 |
| --- | --- |
| [Q&A](<docs/zh/4 常见问题/Q&A.md>) | 模型启动、授权、升级、存储、远程连接和诊断包导出等问题的排查方法 |

## 应用 Demo

`demos/` 文件夹用于存放基于 VLX 系列模型开发的可运行应用示例。每个 Demo 使用独立子目录，可以包含前端、后端、部署配置和使用说明，主要用于验证模型接口、了解集成流程，以及将 VLX 模型适配到具体的边缘设备场景。

目前仓库中只有一个 Demo：

- **`usb_camera_seek_web`** —— 完整的 VLX-Seek 前后端示例。浏览器端选择 USB 摄像头和目标类别，Python 后端采集图像帧、调用 Seek 接口，并通过 WebSocket 返回检测文本和边界框。支持本地运行、Docker 部署，以及无模型服务时的模拟模式。

```text
demos/
└── usb_camera_seek_web/
    ├── src/                 # React + TypeScript 前端
    ├── backend/             # FastAPI 后端、摄像头采集和 Seek 客户端
    ├── docker-compose.yml   # 前后端容器编排配置
    ├── Dockerfile.web       # 前端生产镜像构建文件
    ├── nginx.conf           # 静态资源托管和后端代理配置
    ├── package.json         # 前端依赖及开发、构建命令
    └── README.md            # Demo 的独立安装和使用说明
```

### `usb_camera_seek_web`：VLX-Seek Studio

#### 功能

- 发现并连接 USB 摄像头
- 按检测周期向 VLX-Seek 提交摄像头图像帧
- 输入 `person`、`vehicle`、`red helmet` 等开放词表目标
- 实时显示模型文本和目标边界框
- 暂停、继续和停止检测会话
- 支持真实 Seek 服务或使用 `SEEK_MOCK=1` 进行界面测试

#### 环境要求

- Node.js 18 或更高版本及 npm
- Python 3.10 或更高版本
- 用于真实采集的 Linux 主机，以及可访问的 `/dev/video*` USB 摄像头
- 兼容 VLX-Seek 的 HTTP 接口（OpenAI 兼容的 Chat Completions API）

#### 本地运行

先在一个终端启动后端：

```bash
cd demos/usb_camera_seek_web/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

再在另一个终端启动前端：

```bash
cd demos/usb_camera_seek_web
npm install
npm run dev
```

浏览器访问 <http://localhost:5173>。Vite 开发服务器会根据项目配置转发 `/api` 请求。

没有模型服务时，可以使用模拟模式：

```bash
SEEK_MOCK=1 uvicorn app.main:app --reload --port 8000
```

#### 配置项

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VLX_API_ENABLED` | `true` | 是否启用 VLX SDK 客户端 |
| `VLX_API_ENDPOINT` | `http://172.16.37.118:8000/os/` | SDK 使用的 VLX API 网关地址 |
| `VLX_API_KEY` | 与 `demo.py` 一致 | 用于 Bearer 鉴权的 VLX API 访问密钥 |
| `VLX_API_CONNECT_TIMEOUT_MS` | `60000` | SDK 连接超时时间，单位毫秒 |
| `VLX_API_READ_TIMEOUT_MS` | `60000` | SDK 响应读取超时时间，单位毫秒 |
| `VLX_API_WRITE_TIMEOUT_MS` | `60000` | SDK 写入超时时间，单位毫秒 |
| `SEEK_MODEL` | `vlx-seek-1.5-3b` | 请求中使用的模型 ID |
| `SEEK_ANALYSIS_FPS` | `1` | 每秒最大检测次数 |
| `SEEK_PREVIEW_DELAY_MS` | `500` | 摄像头预览延迟，单位毫秒 |
| `SEEK_MOCK` | `0` | 设置为 `1`、`true` 或 `yes` 时返回模拟结果 |

Docker 部署：

```bash
cd demos/usb_camera_seek_web
docker compose up --build
```

Web 界面地址为 <http://127.0.0.1:5173>。Compose 默认映射 `/dev/video0`，如需使用其他摄像头，可设置 `VIDEO_DEVICE`。

## Seek SDK 集成

后端使用 `omai==1.0.3` Python SDK，通过 `VlxApiClient.from_env()` 创建客户端，使用 SDK 的类型化请求类构造多模态请求，并在工作线程中调用 `vlx_api_client.vlx_seek(request)`。响应中的检测文本来自 `choices[].message.content`，边界框来自 `choices[].result_bbox_list`。

## 文档

- [英文文档](docs/en/)
- [中文文档](docs/zh/)
- [VLX-Seek API 指南](<docs/en/3 Algorithm Application Development/3.1 Model Development APIs/3.1.2 VLX-Seek.md>)
- [VLX-Seek Studio 指南](demos/usb_camera_seek_web/README.md)

## 开发检查

运行后端测试：

```bash
PYTHONPATH=demos/usb_camera_seek_web/backend \
  python -m unittest discover -s demos/usb_camera_seek_web/backend/tests
```

构建前端：

```bash
cd demos/usb_camera_seek_web
npm install
npm run build
```

## 许可与支持

将开发套件用于生产环境前，请先确认随附文档和模型分发条款。如需产品、集成或技术支持，请通过所在组织的支持渠道联系 VLX 项目团队。
