# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

本地部署智能照片管理系统 — a privacy-first, fully offline photo management app. All AI processing (YOLOv8 object tagging, CLIP semantic search, InsightFace face clustering) runs locally with no cloud APIs.

## Commands

### Run the app
```bash
python main.py              # Start on http://127.0.0.1:8000
python main.py --port 9000  # Custom port
```
On Windows, `start.bat` handles venv creation and dependency installation automatically.

### Frontend development
```bash
cd frontend
npm install
npm run dev     # Vite dev server on :5173, proxies /api to localhost:8000
npm run build   # Build to frontend/dist/
```

### No test suite
There are no tests configured in this project. No test framework is set up for either backend or frontend.

## Architecture

### Deployment model
Monorepo deployed as a single unit. FastAPI serves both the REST API (`/api/v1/`) and the built Vue SPA from `frontend/dist/`. In dev, Vite proxies `/api` to the backend.

### Backend (`backend/`)
- **Framework**: FastAPI + uvicorn, app factory in `backend/app.py` (`create_app()`)
- **ORM**: SQLModel (SQLAlchemy + Pydantic), 9 models in `backend/models/`, SQLite at `data/photo_manager.db` with WAL mode
- **DB migrations**: Inline `ALTER TABLE` with try/except in `database.py:init_db()` — no migration tool
- **Routers**: `backend/routers/` — libraries, photos, tags, albums, faces, system
- **Services**: `backend/services/` — scanner, exif_parser, thumbnail, tag_generator, search_engine, duplicate_detector, clip_service, face_service
- **Async tasks**: Thread-based task manager in `backend/tasks/task_manager.py` using `threading.Event` for cancellation, no external broker
- **WebSocket**: `ConnectionManager` in `app.py` broadcasts progress updates to frontend; `_broadcast_sync` wraps thread-safe broadcasting from sync task threads
- **Config**: `config/settings.py` using pydantic-settings

### Frontend (`frontend/`)
- **Framework**: Vue 3 Composition API (`<script setup>`), TypeScript, Vite
- **Routing**: Hash-based (`createWebHashHistory`), 13 lazy-loaded routes
- **State**: Pinia stores in `frontend/src/stores/` — photo, library, tag, album, system
- **UI**: Element Plus (Chinese locale), visionOS-inspired glassmorphism design with light/dark theme
- **Key libs**: photoswipe (image viewer), leaflet (map), vue-virtual-scroller (large lists)
- **API layer**: Axios modules in `frontend/src/api/` with shared client

### Data flow
Frontend Axios → `/api/v1/*` → FastAPI router → service layer → SQLModel → SQLite. Long-running tasks (scan, AI processing) run in background threads and push progress via WebSocket.

## Conventions

- Commit messages follow conventional commits in Chinese: `feat:`, `fix:` with Chinese descriptions
- All user-facing strings are in Chinese
- Python backend uses synchronous code in services (threaded), async only at the FastAPI router level
- Frontend uses `<script setup>` + Composition API exclusively, no Options API
- CSS uses custom properties for theming; styles are in `frontend/src/styles/`
