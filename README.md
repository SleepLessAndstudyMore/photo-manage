<div align="center">

# 📷 智能照片管理系统

**隐私优先 · 完全离线 · AI 驱动的本地照片管理**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.5%2B-green)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-teal)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## ✨ 简介

一个**完全本地部署**的智能照片管理系统，所有 AI 处理（物体识别、语义搜索、人脸聚类）均在本地运行，**无需连接任何云端 API**，彻底保护您的照片隐私。

系统采用前后端分离架构，后端基于 FastAPI 提供高性能 REST API，前端使用 Vue 3 + TypeScript 构建现代化交互界面，支持时间线浏览、智能搜索、地图定位、人脸聚类、重复检测等丰富功能。

## 🚀 核心功能

| 功能 | 描述 | 技术 |
|------|------|------|
| 🏷️ **AI 智能标签** | 自动识别照片中的物体并生成中文标签 | YOLOv8 + COCO 数据集 |
| 🔍 **语义搜索** | 用自然语言描述搜索照片（如"夕阳下的海滩"） | OpenAI CLIP 模型 |
| 👤 **人脸聚类** | 自动检测人脸并按身份分组 | InsightFace + DBSCAN |
| 🗺️ **地图视图** | 在地图上查看照片拍摄位置 | Leaflet + EXIF GPS |
| 🔄 **重复检测** | 基于感知哈希检测重复/相似照片 | imagehash phash |
| 📁 **多库管理** | 支持添加多个照片目录作为独立图库 | SQLite WAL 模式 |
| 🌓 **深色模式** | visionOS 风格毛玻璃设计，支持明暗主题 | CSS 自定义属性 |
| 📊 **实时进度** | WebSocket 推送扫描/AI 处理进度 | 原生 WebSocket |

## 📸 界面预览

- **时间线** — 按日期瀑布流浏览所有照片
- **文件夹** — 按目录结构查看照片
- **搜索** — 关键词搜索 + CLIP 语义搜索
- **地图** — GPS 位置聚合展示
- **人物** — 自动聚类的人脸分组
- **标签** — AI 识别的物体标签云
- **相册** — 自定义照片合集
- **重复照片** — 智能检测重复/相似内容
- **设置** — 图库管理、系统状态、清理工具

## 🛠️ 技术栈

### 后端
- **[FastAPI](https://fastapi.tiangolo.com/)** — 高性能异步 Web 框架
- **[SQLModel](https://sqlmodel.tiangolo.com/)** — SQLAlchemy + Pydantic 的 ORM
- **[SQLite](https://www.sqlite.org/)** — 本地数据库，支持 WAL 模式
- **[Uvicorn](https://www.uvicorn.org/)** — ASGI 服务器

### AI 引擎
- **[YOLOv8](https://docs.ultralytics.com/)** — 实时物体检测与标签生成
- **[OpenAI CLIP](https://github.com/openai/CLIP)** — 图文语义理解与向量检索
- **[InsightFace](https://github.com/deepinsight/insightface)** — 人脸识别与特征提取
- **[DBSCAN](https://scikit-learn.org/)** — 人脸特征聚类

### 前端
- **[Vue 3](https://vuejs.org/)** — Composition API + `<script setup>`
- **[TypeScript](https://www.typescriptlang.org/)** — 类型安全
- **[Vite](https://vitejs.dev/)** — 极速构建工具
- **[Pinia](https://pinia.vuejs.org/)** — 状态管理
- **[Element Plus](https://element-plus.org/)** — UI 组件库（中文 locale）
- **[PhotoSwipe](https://photoswipe.com/)** — 图片灯箱浏览
- **[Leaflet](https://leafletjs.com/)** — 交互式地图
- **[vue-virtual-scroller](https://github.com/Akryum/vue-virtual-scroller)** — 虚拟滚动（大列表性能优化）

## 📦 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+（前端开发/构建需要）
- 推荐 8GB+ 内存（AI 模型加载）

### 一键启动（Windows）

```bash
# 自动创建虚拟环境、安装依赖并启动
start.bat
```

### 手动安装

**1. 克隆仓库**
```bash
git clone https://github.com/SleepLessAndstudyMore/photo-manage.git
cd photo-manage
```

**2. 安装 Python 依赖**
```bash
pip install -r requirements.txt
```

**3. 构建前端（生产环境）**
```bash
cd frontend
npm install
npm run build
cd ..
```

**4. 启动服务**
```bash
python main.py
```

服务启动后会自动打开浏览器访问 `http://127.0.0.1:8000`。Windows 环境下还会显示系统托盘图标。

### 开发模式

```bash
# 终端 1：启动后端
python main.py

# 终端 2：启动前端开发服务器
cd frontend
npm run dev
```

前端开发服务器运行在 `http://localhost:5173`，会自动代理 `/api` 到后端。

### 自定义端口

```bash
python main.py --port 9000
```

## 🏗️ 项目结构

```
photo-manage/
├── backend/                 # Python 后端
│   ├── app.py               # FastAPI 应用工厂 + WebSocket
│   ├── database.py          # 数据库初始化与管理
│   ├── models/              # SQLModel 数据模型（9个实体）
│   ├── routers/             # API 路由（6个模块）
│   ├── services/            # 业务服务层（8个模块）
│   └── tasks/               # 后台任务管理器
├── config/
│   └── settings.py          # Pydantic Settings 配置
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── api/             # Axios API 客户端
│   │   ├── components/      # 公共组件
│   │   ├── router/          # 路由配置（13个懒加载路由）
│   │   ├── stores/          # Pinia 状态管理（5个 store）
│   │   ├── styles/          # CSS 主题变量
│   │   └── views/           # 页面视图（13个页面）
│   └── package.json
├── data/                    # 数据库与配置文件
├── thumbnails/              # 缩略图缓存
├── models/                  # AI 模型文件
├── main.py                  # 应用入口
└── start.bat                # Windows 一键启动脚本
```

## 📋 数据模型

| 实体 | 说明 |
|------|------|
| `Photo` | 照片元数据（路径、EXIF、哈希） |
| `Tag` | AI 识别标签（中英文） |
| `Album` | 用户自定义相册 |
| `FaceCluster` | 人脸聚类分组 |
| `PhotoTag` | 照片-标签关联 |
| `PhotoAlbum` | 照片-相册关联 |
| `PhotoFace` | 照片-人脸检测记录 |
| `PhotoEmbedding` | CLIP 语义向量 |
| `LibrarySource` | 图库目录配置 |

## 🔧 配置

通过 `.env` 文件或环境变量进行配置：

```env
# 服务端口号
PORT=8000

# HuggingFace Token（用于下载 CLIP 模型）
HF_TOKEN=your_token_here
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feat/新功能`
3. 提交更改：`git commit -m "feat: 新增功能描述"`
4. 推送分支：`git push origin feat/新功能`
5. 创建 Pull Request

## 📄 开源许可

本项目基于 [MIT License](LICENSE) 开源。

## 🙏 致谢

- [Ultralytics](https://github.com/ultralytics/ultralytics) — YOLOv8
- [OpenAI](https://github.com/openai/CLIP) — CLIP 模型
- [InsightFace](https://github.com/deepinsight/insightface) — 人脸识别
- [Element Plus](https://github.com/element-plus/element-plus) — UI 组件库
