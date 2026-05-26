import sys
import threading
import webbrowser
import argparse
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.staticfiles import StaticFiles

from config.settings import settings
from backend.app import create_app


def ensure_dirs():
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
    settings.MODEL_DIR.mkdir(parents=True, exist_ok=True)


def open_browser():
    import time
    time.sleep(1.5)
    webbrowser.open(f"http://{settings.HOST}:{settings.PORT}")


def run_tray_icon(server_ref):
    try:
        import pystray
        from PIL import Image

        icon_path = Path(__file__).resolve().parent / "assets" / "tray_icon.png"
        img = Image.open(icon_path)

        def on_exit(icon, item):
            server_ref.should_exit = True
            icon.stop()

        menu = pystray.Menu(
            pystray.MenuItem(
                "打开界面",
                lambda: webbrowser.open(f"http://{settings.HOST}:{settings.PORT}"),
            ),
            pystray.MenuItem("停止服务", on_exit),
        )
        icon = pystray.Icon("PhotoManager", img, "照片管理系统", menu)
        icon.run()
    except Exception:
        pass  # Gracefully degrade if pystray fails (headless env)


def main():
    parser = argparse.ArgumentParser(description="智能照片管理系统")
    parser.add_argument("--port", type=int, default=None, help="服务端口号")
    args = parser.parse_args()

    if args.port is not None:
        settings.PORT = args.port

    ensure_dirs()

    # 数据库完整性检查
    from backend.database import check_database_integrity
    issues = check_database_integrity()
    if issues:
        import logging
        logging.warning(f"数据库完整性检查发现 {len(issues)} 个问题: {issues}")
        print(f"[提示] 数据库完整性检查发现 {len(issues)} 个问题。如果遇到异常，请删除 data/photo_manager.db 后重新扫描。")

    app = create_app()

    # Mount frontend static files — must be after API routes
    frontend_dist = Path(settings.FRONTEND_DIST)
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    import uvicorn

    config = uvicorn.Config(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)

    threading.Thread(target=open_browser, daemon=True).start()
    threading.Thread(target=run_tray_icon, args=(server,), daemon=True).start()

    server.run()


if __name__ == "__main__":
    main()
