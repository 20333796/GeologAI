"""
CRUD 操作单元测试

测试数据持久化层，包括：
- UserCRUD: 用户的创建、读取、更新、删除、查询
- ProjectCRUD: 项目的生命周期管理
- WellLogCRUD: 测井数据管理
- PredictionCRUD: 预测结果管理
"""

import pytest
from datetime import datetime, timedelta

from app.crud import UserCRUD, ProjectCRUD, WellLogCRUD, CurveDataCRUD, PredictionCRUD
from app.schemas import UserCreate, UserUpdate, ProjectCreate, ProjectUpdate, WellLogCreate, WellLogUpdate, PredictionCreate
from app.core.security import SecurityUtility


class TestUserCRUD:
    """测试 UserCRUD 操作"""
    
    def test_create_user(self, test_db):
        """测试：创建用户"""
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="NewPass123!",
            real_name="New User"
        )
        
        user = UserCRUD.create(test_db, user_data)
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.real_name == "New User"
        assert user.role == "user"
        assert user.status == "active"
    
    def test_get_user_by_id(self, test_db, test_user):
        """测试：按 ID 获取用户"""
        user = UserCRUD.get_by_id(test_db, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
    
    def test_get_user_by_username(self, test_db, test_user):
        """测试：按用户名获取用户"""
        user = UserCRUD.get_by_username(test_db, test_user.username)
        
        assert user is not None
        assert user.username == test_user.username
    
    def test_get_user_by_email(self, test_db, test_user):
        """测试：按邮箱获取用户"""
        user = UserCRUD.get_by_email(test_db, test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
    
    def test_list_users(self, test_db, test_user, admin_user):
        """测试：列出用户"""
        users = UserCRUD.list_users(test_db, skip=0, limit=10)
        
        assert len(users) >= 2
        usernames = [u.username for u in users]
        assert test_user.username in usernames
        assert admin_user.username in usernames
    
    def test_update_user(self, test_db, test_user):
        """测试：更新用户"""
        user_update = UserUpdate(real_name="Updated Name")
        updated_user = UserCRUD.update(test_db, test_user.id, user_update)
        
        assert updated_user.real_name == "Updated Name"
    
    def test_delete_user(self, test_db, test_user):
        """测试：删除用户"""
        user_id = test_user.id
        UserCRUD.delete(test_db, user_id)
        
        deleted_user = UserCRUD.get_by_id(test_db, user_id)
        assert deleted_user is None
    
    def test_change_user_status(self, test_db, test_user):
        """测试：改变用户状态"""
        updated_user = UserCRUD.change_status(test_db, test_user.id, "inactive")
        
        assert updated_user.status == "inactive"
    
    def test_count_users(self, test_db, test_user, admin_user):
        """测试：计数用户"""
        count = UserCRUD.count(test_db)
        
        assert count >= 2


class TestProjectCRUD:
    """测试 ProjectCRUD 操作"""
    
    def test_create_project(self, test_db, test_user, test_project_data):
        """测试：创建项目"""
        project_data = ProjectCreate(**test_project_data)
        project = ProjectCRUD.create(test_db, project_data, test_user.id)
        
        assert project.id is not None
        assert project.name == test_project_data["name"]
        assert project.owner_id == test_user.id
        assert project.status == "planning"
    
    def test_get_project_by_id(self, test_db, test_project):
        """测试：按 ID 获取项目"""
        project = ProjectCRUD.get_by_id(test_db, test_project.id)
        
        assert project is not None
        assert project.id == test_project.id
        assert project.name == test_project.name
    
    def test_get_project_by_owner(self, test_db, test_user, test_project):
        """测试：按所有者获取项目"""
        projects = ProjectCRUD.get_by_owner(test_db, test_user.id)
        
        assert len(projects) >= 1
        assert any(p.id == test_project.id for p in projects)
    
    def test_update_project(self, test_db, test_project):
        """测试：更新项目"""
        project_update = ProjectUpdate(description="Updated description")
        updated_project = ProjectCRUD.update(test_db, test_project.id, project_update)
        
        assert updated_project.description == "Updated description"
    
    def test_delete_project(self, test_db, test_project):
        """测试：删除项目"""
        project_id = test_project.id
        ProjectCRUD.delete(test_db, project_id)
        
        deleted_project = ProjectCRUD.get_by_id(test_db, project_id)
        assert deleted_project is None
    
    def test_change_project_status(self, test_db, test_project):
        """测试：改变项目状态"""
        updated_project = ProjectCRUD.change_status(test_db, test_project.id, "completed")
        
        assert updated_project.status == "completed"
    
    def test_count_projects(self, test_db, test_project):
        """测试：计数项目"""
        count = ProjectCRUD.count(test_db)
        
        assert count >= 1
    
    def test_count_projects_by_owner(self, test_db, test_user, test_project):
        """测试：按所有者计数项目"""
        count = ProjectCRUD.count_by_owner(test_db, test_user.id)
        
        assert count >= 1


class TestWellLogCRUD:
    """测试 WellLogCRUD 操作"""
    
    def test_create_well_log(self, test_db, test_project):
        """测试：创建测井"""
        log_data = WellLogCreate(
            filename="new_log.las",
            file_path="/new/new_log.las",
            file_size=51200,
            depth_from=0.0,
            depth_to=1500.0
        )
        log = WellLogCRUD.create(test_db, log_data, test_project.id)
        
        assert log.id is not None
        assert log.filename == "new_log.las"
        assert log.project_id == test_project.id
    
    def test_get_well_log_by_id(self, test_db, test_well_log):
        """测试：按 ID 获取测井"""
        log = WellLogCRUD.get_by_id(test_db, test_well_log.id)
        
        assert log is not None
        assert log.id == test_well_log.id
    
    def test_get_well_log_by_project(self, test_db, test_project, test_well_log):
        """测试：按项目获取测井"""
        logs = WellLogCRUD.get_by_project(test_db, test_project.id)
        
        assert len(logs) >= 1
        assert any(l.id == test_well_log.id for l in logs)
    
    def test_delete_well_log(self, test_db, test_well_log):
        """测试：删除测井"""
        log_id = test_well_log.id
        WellLogCRUD.delete(test_db, log_id)
        
        deleted_log = WellLogCRUD.get_by_id(test_db, log_id)
        assert deleted_log is None
    
    def test_count_well_logs(self, test_db, test_well_log):
        """测试：计数测井"""
        count = WellLogCRUD.count(test_db)
        
        assert count >= 1
    
    def test_count_well_logs_by_project(self, test_db, test_project, test_well_log):
        """测试：按项目计数测井"""
        count = WellLogCRUD.count_by_project(test_db, test_project.id)
        
        assert count >= 1


class TestCurveDataCRUD:
    """测试 CurveDataCRUD 操作"""
    
    def test_count_curves_by_log(self, test_db, test_well_log, test_curve_data):
        """测试：按测井计数曲线"""
        count = CurveDataCRUD.count_by_log(test_db, test_well_log.id)
        
        assert count == len(test_curve_data)
    
    def test_get_curve_by_name(self, test_db, test_well_log, test_curve_data):
        """测试：按名称获取曲线"""
        curves = CurveDataCRUD.get_by_curve_name(test_db, test_well_log.id, "GR")
        
        assert len(curves) > 0
        assert all(c.curve_name == "GR" for c in curves)
    
    def test_delete_curves_by_log(self, test_db, test_well_log, test_curve_data):
        """测试：按测井删除曲线"""
        CurveDataCRUD.delete_by_log(test_db, test_well_log.id)
        
        count = CurveDataCRUD.count_by_log(test_db, test_well_log.id)
        assert count == 0


class TestPredictionCRUD:
    """测试 PredictionCRUD 操作"""
    
    def test_create_prediction(self, test_db, test_well_log, test_ai_model):
        """测试：创建预测"""
        pred_data = PredictionCreate(
            log_id=test_well_log.id,
            model_id=test_ai_model.id,
            results_json={"prediction": [1, 2, 3]},
            confidence=0.95,
            execution_time=3.5
        )
        prediction = PredictionCRUD.create(test_db, pred_data)
        
        assert prediction.id is not None
        assert prediction.log_id == test_well_log.id
        assert prediction.model_id == test_ai_model.id
    
    def test_get_prediction_by_id(self, test_db, test_prediction):
        """测试：按 ID 获取预测"""
        prediction = PredictionCRUD.get_by_id(test_db, test_prediction.id)
        
        assert prediction is not None
        assert prediction.id == test_prediction.id
    
    def test_get_predictions_by_log(self, test_db, test_well_log, test_prediction):
        """测试：按测井获取预测"""
        predictions = PredictionCRUD.get_by_log(test_db, test_well_log.id)
        
        assert len(predictions) >= 1
        assert any(p.id == test_prediction.id for p in predictions)
    
    def test_count_predictions_by_log(self, test_db, test_well_log, test_prediction):
        """测试：按测井计数预测"""
        count = PredictionCRUD.count_by_log(test_db, test_well_log.id)
        
        assert count >= 1
    
    def test_delete_prediction(self, test_db, test_prediction):
        """测试：删除预测"""
        pred_id = test_prediction.id
        PredictionCRUD.delete(test_db, pred_id)
        
        deleted_pred = PredictionCRUD.get_by_id(test_db, pred_id)
        assert deleted_pred is None
