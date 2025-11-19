"""
Service 层业务逻辑单元测试

测试高级业务操作，包括：
- UserService: 用户管理、认证、资料更新
- ProjectService: 项目生命周期管理
- DataService: 测井数据管理、分析
- PredictionService: 预测管理、模型验证
"""

import pytest
from app.services import UserService, ProjectService, DataService, PredictionService
from app.schemas import UserCreate, UserUpdate, ProjectCreate, WellLogCreate, PredictionCreate


class TestUserService:
    """测试 UserService 业务逻辑"""
    
    def test_register_user_success(self, test_db):
        """测试：成功注册用户"""
        result = UserService.register_user(
            db=test_db,
            username="newuser",
            email="new@example.com",
            password="NewPass123!",
            full_name="New User"
        )
        
        assert result.get("success") == True
        assert result.get("user") is not None
        assert result.get("user").username == "newuser"
    
    def test_register_user_duplicate_username(self, test_db, test_user):
        """测试：用户名重复时应返回错误"""
        result = UserService.register_user(
            db=test_db,
            username=test_user.username,
            email="different@example.com",
            password="Pass123!",
            full_name="Different User"
        )
        
        assert result.get("success") == False
        assert result.get("error") == "user_exists"
    
    def test_authenticate_user_success(self, test_db, test_user, test_user_data):
        """测试：成功认证用户"""
        result = UserService.authenticate_user(
            db=test_db,
            username=test_user.username,
            password=test_user_data["password"]
        )
        
        assert result.get("success") == True
        assert result.get("token") is not None
    
    def test_authenticate_user_wrong_password(self, test_db, test_user):
        """测试：密码错误时认证失败"""
        result = UserService.authenticate_user(
            db=test_db,
            username=test_user.username,
            password="WrongPassword"
        )
        
        assert result.get("success") == False
        assert result.get("error") == "invalid_password"
    
    def test_get_user_profile(self, test_db, test_user):
        """测试：获取用户资料"""
        result = UserService.get_user_profile(db=test_db, user_id=test_user.id)
        
        assert result.get("success") == True
        assert result.get("user") is not None
        assert result.get("user")["username"] == test_user.username
    
    def test_change_password_success(self, test_db, test_user, test_user_data):
        """测试：成功修改密码"""
        result = UserService.change_password(
            db=test_db,
            user_id=test_user.id,
            old_password=test_user_data["password"],
            new_password="NewPassword456!"
        )
        
        assert result.get("success") == True
    
    def test_change_password_wrong_old_password(self, test_db, test_user):
        """测试：旧密码错误时修改失败"""
        result = UserService.change_password(
            db=test_db,
            user_id=test_user.id,
            old_password="WrongPassword",
            new_password="NewPassword456!"
        )
        
        assert result.get("success") == False
        assert result.get("error") == "invalid_password"
    
    def test_deactivate_account(self, test_db, test_user):
        """测试：禁用账户"""
        result = UserService.deactivate_account(db=test_db, user_id=test_user.id)
        
        assert result.get("success") == True


class TestProjectService:
    """测试 ProjectService 业务逻辑"""
    
    def test_create_project_success(self, test_db, test_user, test_project_data):
        """测试：成功创建项目"""
        project_create = ProjectCreate(**test_project_data)
        result = ProjectService.create_project(
            db=test_db,
            user_id=test_user.id,
            project_data=project_create
        )
        
        assert result.get("success") == True
        assert result.get("project") is not None
        assert result.get("project").name == test_project_data["name"]
    
    def test_create_project_duplicate_name(self, test_db, test_user, test_project_data):
        """测试：项目名称重复时应返回错误"""
        project_create = ProjectCreate(**test_project_data)
        
        # 创建第一个项目
        result1 = ProjectService.create_project(
            db=test_db,
            user_id=test_user.id,
            project_data=project_create
        )
        assert result1.get("success") == True
        
        # 创建同名项目应失败
        result2 = ProjectService.create_project(
            db=test_db,
            user_id=test_user.id,
            project_data=project_create
        )
        assert result2.get("success") == False
        assert result2.get("error") == "project_exists"
    
    def test_get_project_details(self, test_db, test_project):
        """测试：获取项目详情"""
        result = ProjectService.get_project_details(db=test_db, project_id=test_project.id)
        
        assert result.get("success") == True
        assert result.get("project") is not None
    
    def test_update_project(self, test_db, test_project):
        """测试：更新项目"""
        project_update = ProjectUpdate(description="Updated description")
        result = ProjectService.update_project(
            db=test_db,
            project_id=test_project.id,
            project_update=project_update
        )
        
        assert result.get("success") == True
    
    def test_get_project_statistics(self, test_db, test_project):
        """测试：获取项目统计"""
        result = ProjectService.get_project_statistics(db=test_db, project_id=test_project.id)
        
        assert result.get("success") == True
        assert result.get("statistics") is not None
    
    def test_archive_project(self, test_db, test_project):
        """测试：存档项目"""
        result = ProjectService.archive_project(db=test_db, project_id=test_project.id)
        
        assert result.get("success") == True


class TestDataService:
    """测试 DataService 业务逻辑"""
    
    def test_upload_well_log_success(self, test_db, test_project):
        """测试：成功上传测井"""
        log_data = WellLogCreate(
            filename="new_log.las",
            file_path="/new/new_log.las",
            file_size=51200,
            depth_from=0.0,
            depth_to=1500.0
        )
        result = DataService.upload_well_log(
            db=test_db,
            project_id=test_project.id,
            log_data=log_data
        )
        
        assert result.get("success") == True
        assert result.get("log") is not None
    
    def test_upload_well_log_file_too_large(self, test_db, test_project):
        """测试：文件过大时应返回错误"""
        log_data = WellLogCreate(
            filename="huge_log.las",
            file_path="/huge/huge_log.las",
            file_size=110 * 1024 * 1024,  # 110MB，超过 100MB 限制
            depth_from=0.0,
            depth_to=1500.0
        )
        result = DataService.upload_well_log(
            db=test_db,
            project_id=test_project.id,
            log_data=log_data
        )
        
        assert result.get("success") == False
        assert result.get("error") == "file_too_large"
    
    def test_get_log_summary(self, test_db, test_well_log):
        """测试：获取测井摘要"""
        result = DataService.get_log_summary(db=test_db, log_id=test_well_log.id)
        
        assert result.get("success") == True
        assert result.get("summary") is not None
    
    def test_analyze_log_statistics(self, test_db, test_well_log):
        """测试：分析测井统计"""
        result = DataService.analyze_log_statistics(db=test_db, log_id=test_well_log.id)
        
        assert result.get("success") == True
        assert result.get("statistics") is not None
    
    def test_delete_log_with_data(self, test_db, test_well_log):
        """测试：删除测井及关联数据"""
        result = DataService.delete_log_with_data(db=test_db, log_id=test_well_log.id)
        
        assert result.get("success") == True


class TestPredictionService:
    """测试 PredictionService 业务逻辑"""
    
    def test_create_prediction_success(self, test_db, test_well_log, test_ai_model):
        """测试：成功创建预测"""
        pred_data = PredictionCreate(
            log_id=test_well_log.id,
            model_id=test_ai_model.id,
            results_json='{"prediction": [1, 2, 3]}',
            confidence=0.95,
            execution_time=3.5
        )
        result = PredictionService.create_prediction(db=test_db, prediction_data=pred_data)
        
        assert result.get("success") == True
        assert result.get("prediction") is not None
    
    def test_create_prediction_invalid_confidence(self, test_db, test_well_log, test_ai_model):
        """测试：置信度无效时创建失败"""
        pred_data = PredictionCreate(
            log_id=test_well_log.id,
            model_id=test_ai_model.id,
            results_json='{"prediction": [1, 2, 3]}',
            confidence=1.5,  # 无效，超过 1.0
            execution_time=3.5
        )
        result = PredictionService.create_prediction(db=test_db, prediction_data=pred_data)
        
        assert result.get("success") == False
        assert result.get("error") == "invalid_confidence"
    
    def test_get_prediction_details(self, test_db, test_prediction):
        """测试：获取预测详情"""
        result = PredictionService.get_prediction_details(
            db=test_db,
            prediction_id=test_prediction.id
        )
        
        assert result.get("success") == True
        assert result.get("prediction") is not None
    
    def test_rerun_prediction(self, test_db, test_prediction):
        """测试：重新运行预测"""
        result = PredictionService.rerun_prediction(
            db=test_db,
            prediction_id=test_prediction.id
        )
        
        assert result.get("success") == True
        assert result.get("new_prediction") is not None
    
    def test_get_model_statistics(self, test_db, test_ai_model, test_prediction):
        """测试：获取模型统计"""
        result = PredictionService.get_model_statistics(
            db=test_db,
            model_id=test_ai_model.id
        )
        
        assert result.get("success") == True
        assert result.get("statistics") is not None


# ==================== 错误场景测试 ====================

class TestErrorHandling:
    """测试错误处理机制"""
    
    def test_get_nonexistent_user(self, test_db):
        """测试：获取不存在的用户"""
        result = UserService.get_user_profile(db=test_db, user_id=99999)
        
        assert result.get("success") == False
        assert result.get("error") == "user_not_found"
    
    def test_get_nonexistent_project(self, test_db):
        """测试：获取不存在的项目"""
        result = ProjectService.get_project_details(db=test_db, project_id=99999)
        
        assert result.get("success") == False
        assert result.get("error") == "project_not_found"
    
    def test_delete_nonexistent_prediction(self, test_db):
        """测试：删除不存在的预测"""
        result = PredictionService.delete_prediction(db=test_db, prediction_id=99999)
        
        assert result.get("success") == False
        assert result.get("error") == "prediction_not_found"


from app.schemas import ProjectUpdate
