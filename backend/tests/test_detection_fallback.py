import shutil
import sys
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageDraw


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from app.core.rtdetr_detector import RTDETRDetector
from app.extensions import db
from flask import g
import app.models  # noqa: F401
from app.models.model_version import ModelVersion
from app.models.sys_user import SysUser
from app.services.detection_service import DetectionService
from app.services.file_service import FileService


class DetectionFallbackTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.storage_root = BACKEND_ROOT / "tests" / "tmp_storage"
        self.app.config["STORAGE_ROOT"] = self.storage_root
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        db.session.add(
            SysUser(
                id=1,
                username="admin",
                password="hashed",
                real_name="Admin",
                email="admin@test.local",
                phone="13800000001",
                status=1,
                is_deleted=0,
            )
        )
        db.session.add(
            ModelVersion(
                version_code="test-v1",
                model_name="Fallback Detector",
                weight_path="backend/weights/missing-weight-file.pth",
                map_50=0,
                map_50_95=0,
                precision_rate=0,
                recall_rate=0,
                is_active=1,
                description="fallback test",
                create_by=1,
                is_deleted=0,
            )
        )
        db.session.commit()
        self.cleanup_storage()
        RTDETRDetector._model = None
        RTDETRDetector._processor = None
        RTDETRDetector._loaded_weight_path = None

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        self.cleanup_storage()
        RTDETRDetector._model = None
        RTDETRDetector._processor = None
        RTDETRDetector._loaded_weight_path = None

    def cleanup_storage(self):
        if self.storage_root.exists():
            shutil.rmtree(self.storage_root)

    def build_image_bytes(self) -> bytes:
        image = Image.new("RGB", (320, 240), "#8BC34A")
        draw = ImageDraw.Draw(image)
        draw.rectangle((30, 40, 150, 120), fill="#7B5548")
        draw.ellipse((180, 70, 260, 150), fill="#2E7D32")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_detect_saved_image_uses_fallback_when_weight_missing(self):
        raw = self.build_image_bytes()
        relative_path = FileService.save_bytes(raw, "png", result=False)

        result = DetectionService.detect_saved_image(
            user_id=1,
            relative_path=relative_path,
            image_name="fallback.png",
            image_size_bytes=len(raw),
            confidence_threshold=0.25,
            batch_id=None,
            raise_on_error=True,
        )

        self.assertIsInstance(result["record_id"], int)
        self.assertGreaterEqual(result["total_detections"], 1)
        self.assertTrue(result["result_image_url"])
        self.assertTrue(result["results"])

    def test_get_record_includes_image_and_model_metadata(self):
        raw = self.build_image_bytes()
        relative_path = FileService.save_bytes(raw, "png", result=False)
        result = DetectionService.detect_saved_image(
            user_id=1,
            relative_path=relative_path,
            image_name="detail.png",
            image_size_bytes=len(raw),
            confidence_threshold=0.25,
            batch_id=None,
            raise_on_error=True,
        )

        g.current_user = SimpleNamespace(id=1)
        g.current_role = SimpleNamespace(data_scope="DATA_ALL")
        detail = DetectionService.get_record(result["record_id"])

        self.assertEqual(detail["image_size"], len(raw))
        self.assertEqual(detail["image_width"], 320)
        self.assertEqual(detail["image_height"], 240)
        self.assertEqual(detail["model_version_id"], 1)
        self.assertEqual(detail["version_code"], "test-v1")


if __name__ == "__main__":
    unittest.main()
