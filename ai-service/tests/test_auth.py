"""
认证模块单元测试
测试JWT和RBAC功能
"""

import unittest
from datetime import datetime, timedelta


class TestJWTHandler(unittest.TestCase):
    """JWT处理器测试"""

    def setUp(self):
        """设置测试环境"""
        from app.auth.jwt_handler import JWTHandler
        self.jwt_handler = JWTHandler()

    def test_create_access_token(self):
        """测试创建访问令牌"""
        token = self.jwt_handler.create_access_token(
            user_id="test_user",
            username="test_user",
            roles=["admin"]
        )
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        token = self.jwt_handler.create_refresh_token(user_id="test_user")
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_create_token_pair(self):
        """测试创建令牌对"""
        tokens = self.jwt_handler.create_token_pair(
            user_id="test_user",
            username="test_user",
            roles=["admin"]
        )
        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)
        self.assertIn("token_type", tokens)

    def test_verify_access_token(self):
        """测试验证访问令牌"""
        token = self.jwt_handler.create_access_token(
            user_id="test_user",
            username="test_user",
            roles=["admin"]
        )
        success, payload, error = self.jwt_handler.verify_access_token(token)
        self.assertTrue(success)
        self.assertEqual(payload["sub"], "test_user")
        self.assertEqual(payload["type"], "access")

    def test_verify_refresh_token(self):
        """测试验证刷新令牌"""
        token = self.jwt_handler.create_refresh_token(user_id="test_user")
        success, payload, error = self.jwt_handler.verify_refresh_token(token)
        self.assertTrue(success)
        self.assertEqual(payload["sub"], "test_user")
        self.assertEqual(payload["type"], "refresh")

    def test_verify_invalid_token(self):
        """测试验证无效令牌"""
        success, payload, error = self.jwt_handler.verify_access_token("invalid_token")
        self.assertFalse(success)
        self.assertIn("Invalid token", error)

    def test_refresh_access_token(self):
        """测试刷新访问令牌"""
        refresh_token = self.jwt_handler.create_refresh_token(user_id="test_user")
        success, result, error = self.jwt_handler.refresh_access_token(refresh_token)
        self.assertTrue(success)
        self.assertIn("access_token", result)

    def test_decode_token(self):
        """测试解码令牌"""
        token = self.jwt_handler.create_access_token(
            user_id="test_user",
            username="test_user",
            roles=["admin"]
        )
        payload = self.jwt_handler.decode_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "test_user")


class TestRBACManager(unittest.TestCase):
    """RBAC管理器测试"""

    def setUp(self):
        """设置测试环境"""
        from app.auth.rbac import RBACManager, Role, Permission
        self.rbac_manager = RBACManager()
        self.Role = Role
        self.Permission = Permission

    def test_get_role_permissions(self):
        """测试获取角色权限"""
        admin_perms = self.rbac_manager.get_role_permissions(self.Role.ADMIN)
        self.assertIn(self.Permission.USER_VIEW, admin_perms)
        self.assertIn(self.Permission.SYSTEM_CONFIG, admin_perms)

        student_perms = self.rbac_manager.get_role_permissions(self.Role.STUDENT)
        self.assertIn(self.Permission.SCHOOL_VIEW, student_perms)
        self.assertNotIn(self.Permission.SYSTEM_CONFIG, student_perms)

    def test_get_user_permissions(self):
        """测试获取用户权限"""
        perms = self.rbac_manager.get_user_permissions(["admin"])
        self.assertIn(self.Permission.USER_VIEW, perms)
        self.assertIn(self.Permission.SYSTEM_CONFIG, perms)

        perms = self.rbac_manager.get_user_permissions(["student"])
        self.assertIn(self.Permission.SCHOOL_VIEW, perms)
        self.assertNotIn(self.Permission.SYSTEM_CONFIG, perms)

    def test_has_permission(self):
        """测试权限检查"""
        self.assertTrue(
            self.rbac_manager.has_permission(["admin"], self.Permission.USER_VIEW)
        )
        self.assertFalse(
            self.rbac_manager.has_permission(["student"], self.Permission.USER_DELETE)
        )

    def test_has_any_permission(self):
        """测试任意权限检查"""
        self.assertTrue(
            self.rbac_manager.has_any_permission(
                ["student"],
                [self.Permission.SCHOOL_VIEW, self.Permission.USER_VIEW]
            )
        )
        self.assertFalse(
            self.rbac_manager.has_any_permission(
                ["student"],
                [self.Permission.USER_DELETE, self.Permission.SYSTEM_CONFIG]
            )
        )

    def test_has_all_permissions(self):
        """测试所有权限检查"""
        self.assertTrue(
            self.rbac_manager.has_all_permissions(
                ["admin"],
                [self.Permission.USER_VIEW, self.Permission.SCHOOL_VIEW]
            )
        )
        self.assertFalse(
            self.rbac_manager.has_all_permissions(
                ["student"],
                [self.Permission.SCHOOL_VIEW, self.Permission.USER_DELETE]
            )
        )

    def test_is_admin(self):
        """测试管理员检查"""
        self.assertTrue(self.rbac_manager.is_admin(["admin"]))
        self.assertFalse(self.rbac_manager.is_admin(["student"]))

    def test_is_teacher(self):
        """测试教师检查"""
        self.assertTrue(self.rbac_manager.is_teacher(["teacher"]))
        self.assertFalse(self.rbac_manager.is_teacher(["student"]))

    def test_is_student(self):
        """测试学生检查"""
        self.assertTrue(self.rbac_manager.is_student(["student"]))
        self.assertFalse(self.rbac_manager.is_student(["teacher"]))


class TestUserContext(unittest.TestCase):
    """用户上下文测试"""

    def setUp(self):
        """设置测试环境"""
        from app.auth.rbac import UserContext
        self.UserContext = UserContext

    def test_user_context_creation(self):
        """测试用户上下文创建"""
        ctx = self.UserContext(
            user_id="test_user",
            username="test_user",
            roles=["admin"]
        )
        self.assertEqual(ctx.user_id, "test_user")
        self.assertEqual(ctx.username, "test_user")
        self.assertEqual(ctx.roles, ["admin"])

    def test_permissions_property(self):
        """测试权限属性"""
        ctx = self.UserContext(
            user_id="test_user",
            username="test_user",
            roles=["admin"]
        )
        perms = ctx.permissions
        self.assertIsNotNone(perms)
        self.assertTrue(len(perms) > 0)

    def test_has_permission(self):
        """测试权限检查"""
        ctx = self.UserContext(
            user_id="test_user",
            username="test_user",
            roles=["admin"]
        )
        from app.auth.rbac import Permission
        self.assertTrue(ctx.has_permission(Permission.USER_VIEW))

    def test_is_admin(self):
        """测试管理员检查"""
        ctx_admin = self.UserContext(
            user_id="admin",
            username="admin",
            roles=["admin"]
        )
        ctx_student = self.UserContext(
            user_id="student",
            username="student",
            roles=["student"]
        )
        self.assertTrue(ctx_admin.is_admin())
        self.assertFalse(ctx_student.is_admin())

    def test_to_dict(self):
        """测试转换为字典"""
        ctx = self.UserContext(
            user_id="test_user",
            username="test_user",
            roles=["admin"]
        )
        data = ctx.to_dict()
        self.assertIn("user_id", data)
        self.assertIn("username", data)
        self.assertIn("roles", data)
        self.assertIn("permissions", data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
