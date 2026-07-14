import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from flask import g

from app import create_app
from app.extensions import db
import app.models  # noqa: F401
from app.models.sys_user import SysUser
from app.services.disease_service import DiseaseService


class DiseaseRecreateTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
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
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_create_disease_reuses_deleted_class_name(self):
        payload = {
            "class_name": "rust",
            "chinese_name": "锈病",
            "alias": "叶锈病",
            "symptom": "叶片出现橙黄色病斑并向四周扩散。",
            "cause": "高湿环境下病原菌快速传播。",
            "prevention": "及时清理病残体并喷施防治药剂。",
            "severity_level": 3,
        }

        with self.app.test_request_context("/api/v1/diseases", method="POST", data={}):
            g.current_user = SimpleNamespace(id=1)
            created = DiseaseService.create_disease(payload, None)
            DiseaseService.delete_disease(created["id"])
            recreated = DiseaseService.create_disease(payload, None)

        self.assertEqual(recreated["class_name"], "rust")
        self.assertEqual(recreated["chinese_name"], "锈病")


if __name__ == "__main__":
    unittest.main()
