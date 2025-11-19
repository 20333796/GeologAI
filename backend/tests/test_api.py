"""
API 端点集成测试

测试 REST API 接口的完整功能，包括：
- 认证端点 (auth)
- 用户端点 (users)
- 项目端点 (projects)
- 数据端点 (data)
- 预测端点 (predictions)
"""

import pytest
import json


class TestAuthEndpoints:
    """测试认证相关端点"""
    
    def test_register_endpoint_success(self, client):
        """测试：用户注册成功"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "NewPass123!",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
    
    def test_register_endpoint_duplicate(self, client, test_user_data):
        """测试：重复注册返回错误"""
        # 第一次注册
        response1 = client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )
        assert response1.status_code == 201
        
        # 第二次注册相同用户
        response2 = client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )
        assert response2.status_code == 400
    
    def test_login_endpoint_success(self, client, test_user_data):
        """测试：用户登录成功"""
        # 先注册
        client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )
        
        # 再登录
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestUserEndpoints:
    """测试用户相关端点"""
    
    def test_get_me_endpoint(self, client, auth_headers):
        """测试：获取当前用户"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_list_users_endpoint(self, client, auth_headers):
        """测试：列出用户"""
        response = client.get("/api/v1/users", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_update_user_endpoint(self, client, auth_headers, test_user):
        """测试：更新用户信息"""
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json={"full_name": "Updated Name"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
    
    def test_change_password_endpoint(self, client, auth_headers, test_user, test_user_data):
        """测试：修改密码"""
        response = client.post(
            f"/api/v1/users/{test_user.id}/change-password",
            json={
                "old_password": test_user_data["password"],
                "new_password": "NewPassword456!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestProjectEndpoints:
    """测试项目相关端点"""
    
    def test_create_project_endpoint(self, client, auth_headers):
        """测试：创建项目"""
        response = client.post(
            "/api/v1/projects",
            json={
                "name": "API Test Project",
                "description": "Created via API",
                "location": "Test Location",
                "depth_from": 0.0,
                "depth_to": 3000.0,
                "well_diameter": 200.0
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test Project"
    
    def test_list_projects_endpoint(self, client, auth_headers):
        """测试：列出项目"""
        response = client.get("/api/v1/projects", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_get_project_endpoint(self, client, auth_headers, test_project):
        """测试：获取项目详情"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project.id
    
    def test_update_project_endpoint(self, client, auth_headers, test_project):
        """测试：更新项目"""
        response = client.put(
            f"/api/v1/projects/{test_project.id}",
            json={"description": "Updated via API"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated via API"
    
    def test_get_project_stats_endpoint(self, client, auth_headers, test_project):
        """测试：获取项目统计"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data


class TestDataEndpoints:
    """测试数据相关端点"""
    
    def test_list_logs_endpoint(self, client, auth_headers):
        """测试：列出测井"""
        response = client.get("/api/v1/data/logs", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_get_log_endpoint(self, client, auth_headers, test_well_log):
        """测试：获取测井详情"""
        response = client.get(
            f"/api/v1/data/logs/{test_well_log.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_well_log.id
    
    def test_create_log_endpoint(self, client, auth_headers, test_project):
        """测试：创建测井"""
        response = client.post(
            "/api/v1/data/logs",
            params={"project_id": test_project.id},
            json={
                "filename": "api_test.las",
                "file_path": "/api/api_test.las",
                "file_size": 51200,
                "depth_from": 0.0,
                "depth_to": 1500.0
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "api_test.las"


class TestPredictionEndpoints:
    """测试预测相关端点"""
    
    def test_list_predictions_endpoint(self, client, auth_headers):
        """测试：列出预测"""
        response = client.get("/api/v1/predictions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_get_prediction_endpoint(self, client, auth_headers, test_prediction):
        """测试：获取预测详情"""
        response = client.get(
            f"/api/v1/predictions/{test_prediction.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_prediction.id
    
    def test_create_prediction_endpoint(self, client, auth_headers, test_well_log, test_ai_model):
        """测试：创建预测"""
        response = client.post(
            "/api/v1/predictions",
            json={
                "log_id": test_well_log.id,
                "model_id": test_ai_model.id,
                "results_json": '{"prediction": [1, 2, 3]}',
                "confidence": 0.95,
                "execution_time": 3.5
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["confidence"] == 0.95
    
    def test_rerun_prediction_endpoint(self, client, auth_headers, test_prediction):
        """测试：重新运行预测"""
        response = client.post(
            f"/api/v1/predictions/{test_prediction.id}/rerun",
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestAuthorizationAndPermissions:
    """测试授权和权限检查"""
    
    def test_unauthenticated_request(self, client):
        """测试：未认证请求返回 401"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """测试：无效令牌返回 401"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_access_other_user_profile(self, client, test_user, admin_user, auth_headers):
        """测试：普通用户无法访问他人资料"""
        response = client.get(
            f"/api/v1/users/{admin_user.id}",
            headers=auth_headers  # 使用 test_user 的令牌
        )
        
        # 根据实现，可能返回 403 或其他错误
        assert response.status_code in [403, 400]


class TestErrorHandlingInAPI:
    """测试 API 错误处理"""
    
    def test_not_found_user(self, client, admin_headers):
        """测试：访问不存在的用户"""
        response = client.get("/api/v1/users/99999", headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_not_found_project(self, client, auth_headers):
        """测试：访问不存在的项目"""
        response = client.get("/api/v1/projects/99999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_invalid_request_data(self, client, auth_headers):
        """测试：无效的请求数据"""
        response = client.post(
            "/api/v1/projects",
            json={
                "name": "Test",
                # 缺少必要字段
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_duplicate_project_name(self, client, auth_headers, test_project):
        """测试：重复的项目名称"""
        response = client.post(
            "/api/v1/projects",
            json={
                "name": test_project.name,
                "description": "Different project",
                "location": "Test",
                "depth_from": 0.0,
                "depth_to": 3000.0,
                "well_diameter": 200.0
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400


class TestDataValidation:
    """测试数据验证"""
    
    def test_invalid_email_format(self, client):
        """测试：无效的邮箱格式"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "Pass123!",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
    
    def test_invalid_confidence_range(self, client, auth_headers, test_well_log, test_ai_model):
        """测试：无效的置信度范围"""
        response = client.post(
            "/api/v1/predictions",
            json={
                "log_id": test_well_log.id,
                "model_id": test_ai_model.id,
                "results_json": "{}",
                "confidence": 1.5,  # 超过 1.0
                "execution_time": 3.5
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
