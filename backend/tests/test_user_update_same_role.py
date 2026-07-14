import sys
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from app.extensions import db
import app.models  # noqa: F401
from app.models.sys_role import SysRole
from app.models.sys_user import SysUser
from app.models.sys_user_role import SysUserRole
from app.services.user_service import UserService


class UserUpdateSameRoleTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        db.session.add(
            SysRole(
                id=1,
                role_code="ROLE_TEST",
                role_name="Test Role",
                data_scope="DATA_SELF",
                description="role for update test",
                status=1,
                is_deleted=0,
            )
        )
        db.session.add(
            SysUser(
                id=1,
                username="user001",
                password="hashed",
                real_name="User One",
                email="user001@test.local",
                phone="13800000001",
                status=1,
                is_deleted=0,
            )
        )
        db.session.add(SysUserRole(user_id=1, role_id=1, is_deleted=0))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_update_user_keeps_same_role_without_duplicate_relation(self):
        with self.app.test_request_context("/api/v1/users/1", method="PUT", json={}):
            result = UserService.update_user(
                1,
                {
                    "real_name": "User One Updated",
                    "email": "user001-updated@test.local",
                    "phone": "13800000002",
                    "role_id": 1,
                    "status": 1,
                },
            )

        active_relations = SysUserRole.query.filter_by(user_id=1, role_id=1, is_deleted=0).count()
        self.assertEqual(result["real_name"], "User One Updated")
        self.assertEqual(result["email"], "user001-updated@test.local")
        self.assertEqual(result["phone"], "13800000002")
        self.assertEqual(result["role_id"], 1)
        self.assertEqual(active_relations, 1)


if __name__ == "__main__":
    unittest.main()
