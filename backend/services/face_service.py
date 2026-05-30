"""Face detection and clustering service using InsightFace + DBSCAN."""
import logging
import os
from pathlib import Path

import numpy as np
from PIL import Image
from sqlmodel import Session, select, func

from config.settings import settings
from backend.models.photo import Photo
from backend.models.photo_face import PhotoFace
from backend.models.face_cluster import FaceCluster
from backend.tasks.task_manager import task_manager, TaskType

logger = logging.getLogger(__name__)

FACE_THUMBNAIL_DIR: Path = settings.THUMBNAIL_DIR / "faces"


class FaceService:
    """InsightFace detection + DBSCAN clustering."""

    def __init__(self, db_session_factory):
        self._session_factory = db_session_factory
        self._app = None
        FACE_THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    def _lazy_load_model(self):
        if self._app is None:
            try:
                import insightface
                from insightface.app import FaceAnalysis
                self._app = FaceAnalysis(name="buffalo_l", root=str(settings.MODEL_DIR))
                self._app.prepare(ctx_id=-1)  # CPU
                logger.info("InsightFace model loaded (buffalo_l)")
            except Exception as e:
                logger.warning(f"Failed to load InsightFace model: {e}")
                self._app = None
        return self._app

    def detect_faces(self, image_path: str) -> list[dict]:
        """Detect faces in a single image. Returns list of face dicts."""
        app = self._lazy_load_model()
        if app is None:
            return []
        try:
            import cv2
            # 使用 imdecode 替代 imread，支持中文路径
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return []
            faces = app.get(img)
            results = []
            for face in faces:
                bbox = face.bbox.astype(int).tolist()  # [x1, y1, x2, y2]
                results.append({
                    "bbox": bbox,
                    "embedding": np.array(face.embedding, dtype=np.float32).tobytes(),
                    "confidence": float(face.det_score),
                })
            return results
        except Exception as e:
            logger.warning(f"Face detection failed for {image_path}: {e}")
            return []

    def _save_face_thumbnail(self, photo_path: str, bbox: list[int], face_id: int) -> str | None:
        """Crop face region and save as thumbnail. Returns relative path."""
        try:
            import cv2
            # 使用与 detect_faces 相同的读取方式，确保坐标一致
            img = cv2.imdecode(np.fromfile(photo_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return None
            x1, y1, x2, y2 = map(int, bbox)
            h, w = img.shape[:2]
            # Add margin
            margin = int((x2 - x1) * 0.3)
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(w, x2 + margin)
            y2 = min(h, y2 + margin)
            face_img = img[y1:y2, x1:x2]
            if face_img.size == 0:
                return None
            face_img = cv2.resize(face_img, (160, 160), interpolation=cv2.INTER_LANCZOS4)

            rel_path = f"faces/{face_id}.jpg"
            abs_path = FACE_THUMBNAIL_DIR / f"{face_id}.jpg"
            # 使用 imencode + tofile 支持中文路径
            _, buf = cv2.imencode('.jpg', face_img)
            buf.tofile(str(abs_path))
            return rel_path
        except Exception as e:
            logger.warning(f"Face thumbnail failed: {e}")
            return None

    def detect_all_faces(
        self, task_info,
        photo_ids: list[int] | None = None,
        source_paths: list[str] | None = None,
        is_videos: list[bool] | None = None,
    ):
        """Background task: detect faces for photos without existing face data.

        If photo_ids/source_paths/is_videos are passed, process only those (from scan).
        Otherwise, query all photos that have no PhotoFace rows.
        """
        app = self._lazy_load_model()
        if app is None:
            logger.warning("InsightFace unavailable, skipping face detection")
            return

        session = self._session_factory()
        try:
            if photo_ids is not None and source_paths is not None:
                # Batch from scanner — process only images
                targets = []
                for pid, spath, is_v in zip(photo_ids, source_paths, is_videos or []):
                    if not is_v:
                        targets.append((pid, spath))
            else:
                # Full scan: find all image photos without faces
                all_photos = session.exec(
                    select(Photo).where(
                        Photo.file_missing == False,  # noqa: E712
                        Photo.is_video == False,  # noqa: E712
                    )
                ).all()
                existing_ids = set(
                    row[0] for row in session.exec(
                        select(PhotoFace.photo_id).distinct()
                    ).all()
                )
                targets = [(p.id, p.file_path) for p in all_photos if p.id not in existing_ids]

            total = len(targets)
            if total == 0:
                logger.info("No new photos to detect faces")
                return

            logger.info(f"Detecting faces for {total} images")
            task_manager.update_progress(
                task_info.id, 0.0, f"人脸检测: 0/{total}"
            )

            for i, (pid, spath) in enumerate(targets):
                if task_info.is_cancelled:
                    return

                try:
                    faces = self.detect_faces(spath)
                    for face_data in faces:
                        pf = PhotoFace(
                            photo_id=pid,
                            bbox_x=face_data["bbox"][0],
                            bbox_y=face_data["bbox"][1],
                            bbox_w=face_data["bbox"][2] - face_data["bbox"][0],
                            bbox_h=face_data["bbox"][3] - face_data["bbox"][1],
                            face_embedding=face_data["embedding"],
                            confidence=face_data["confidence"],
                        )
                        session.add(pf)
                        session.flush()  # get pf.id

                        thumb = self._save_face_thumbnail(
                            spath, face_data["bbox"], pf.id
                        )
                        if thumb:
                            pf.thumbnail_path = thumb
                            session.add(pf)

                    if i % 10 == 0:
                        session.commit()
                except Exception as e:
                    logger.warning(f"Face detection error for {spath}: {e}")
                    session.rollback()

                if i % 10 == 0:
                    task_manager.update_progress(
                        task_info.id,
                        min((i + 1) / max(total, 1), 0.9),
                        f"人脸检测: {i + 1}/{total}",
                    )

            session.commit()

            # Auto-cluster after detection
            task_manager.update_progress(task_info.id, 0.9, "人脸聚类中...")
            self._run_clustering(session, task_info)

            logger.info("Face detection and clustering complete")
            task_manager.update_progress(task_info.id, 1.0, "人脸检测完成")
        finally:
            session.close()

    def _run_clustering(self, session: Session, task_info=None):
        """DBSCAN clustering on all face embeddings. Removes stale clusters first."""
        # Remove all existing clusters (faces get FK set to NULL)
        for old in session.exec(select(FaceCluster)).all():
            session.delete(old)
        session.flush()

        # Clear cluster IDs from all faces
        for pf in session.exec(select(PhotoFace)).all():
            pf.face_cluster_id = None
            session.add(pf)
        session.flush()

        all_faces = session.exec(select(PhotoFace)).all()
        if not all_faces:
            return

        embeddings = []
        face_ids = []
        for pf in all_faces:
            try:
                emb = np.frombuffer(pf.face_embedding, dtype=np.float32)
                embeddings.append(emb)
                face_ids.append(pf.id)
            except Exception:
                continue

        if len(face_ids) == 0:
            return

        if len(face_ids) == 1:
            cluster = FaceCluster(face_count=1)
            session.add(cluster)
            session.flush()
            pf = all_faces[0]
            cluster.representative_face_id = pf.id
            pf.face_cluster_id = cluster.id
            session.add(pf)
            session.add(cluster)
            session.commit()
            return

        X = np.array(embeddings)
        try:
            from sklearn.cluster import DBSCAN
            clustering = DBSCAN(metric="cosine", eps=0.5, min_samples=1).fit(X)
            labels = clustering.labels_
        except Exception as e:
            logger.warning(f"DBSCAN clustering failed: {e}, falling back to single cluster")
            labels = np.zeros(len(face_ids), dtype=int)

        cluster_map: dict[int, list[int]] = {}
        for face_id, label in zip(face_ids, labels):
            cluster_map.setdefault(int(label), []).append(face_id)

        # Assign faces to clusters first
        for label, members in cluster_map.items():
            cluster = FaceCluster(face_count=0)  # placeholder, will update below
            session.add(cluster)
            session.flush()

            representative_id = members[0]
            cluster.representative_face_id = representative_id
            session.add(cluster)

            for fid in members:
                pf = session.get(PhotoFace, fid)
                if pf:
                    pf.face_cluster_id = cluster.id
                    session.add(pf)

        session.commit()

        # Refresh face_count = distinct photo count for each cluster
        for cluster in session.exec(select(FaceCluster)).all():
            photo_count = session.exec(
                select(func.count(PhotoFace.photo_id.distinct()))
                .where(PhotoFace.face_cluster_id == cluster.id)
            ).one()
            cluster.face_count = photo_count or 0
            session.add(cluster)
        session.commit()

    def run_clustering(self, task_info):
        """Public clustering task wrapper."""
        session = self._session_factory()
        try:
            task_manager.update_progress(task_info.id, 0.0, "人脸聚类中...")
            self._run_clustering(session, task_info)
            task_manager.update_progress(task_info.id, 1.0, "人脸聚类完成")
        finally:
            session.close()


# Module-level singleton
_instance: FaceService | None = None


def get_face_service(db_session_factory=None) -> FaceService:
    global _instance
    if _instance is None and db_session_factory is not None:
        _instance = FaceService(db_session_factory)
    return _instance
