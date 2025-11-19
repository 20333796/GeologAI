"""
测试配置和 fixtures

提供共享的测试配置、数据库连接、用户/项目等测试数据。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
import os
from datetime import datetime, timedelta

# 导入应用和模型
from app.main import app
from app.db.session import get_db
from app.models import Base
from app.models import User, Project, WellLog, CurveData, AIModel, Prediction, AuditLog
from app.core.security import SecurityUtility
from app.schemas import UserCreate, ProjectCreate, WellLogCreate, PredictionCreate


# ==================== 数据库配置 ====================

# 测试数据库 URL (使用 SQLite 内存数据库，速度快)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库并返回会话"""
    # 创建引擎
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 需要
        echo=False  # 设置为 True 可看到 SQL 语句
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话工厂
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    # 创建会话
    db = TestingSessionLocal()
    
    yield db
    
    # 清理
    db.close()
    Base.metadata.drop_all(bind=engine)


# ==================== FastAPI 客户端 ====================

@pytest.fixture(scope="function")
def client(test_db):
    """创建 FastAPI 测试客户端"""
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    
    yield client
    
    app.dependency_overrides.clear()


# ==================== 测试数据工厂 ====================

@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "real_name": "Test User"
    }


@pytest.fixture
def test_user(test_db, test_user_data):
    """创建测试用户"""
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password_hash=SecurityUtility.hash_password(test_user_data["password"]),
        real_name=test_user_data["real_name"],
        role="user",
        status="active"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db):
    """创建管理员用户"""
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=SecurityUtility.hash_password("AdminPass123!"),
        real_name="Admin User",
        role="admin",
        status="active"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_project_data():
    """测试项目数据"""
    return {
        "name": "Test Project",
        "description": "A test project",
        "location": "Test Location",
        "depth_from": 0.0,
        "depth_to": 3000.0,
        "well_diameter": 200.0
    }


@pytest.fixture
def test_project(test_db, test_user, test_project_data):
    """创建测试项目"""
    project = Project(
        name=test_project_data["name"],
        description=test_project_data["description"],
        location=test_project_data["location"],
        depth_from=test_project_data["depth_from"],
        depth_to=test_project_data["depth_to"],
        well_diameter=test_project_data["well_diameter"],
        owner_id=test_user.id,
        status="planning"
    )
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    return project


@pytest.fixture
def test_well_log(test_db, test_project):
    """创建测试测井"""
    log = WellLog(
        filename="test_log.las",
        file_path="/test/test_log.las",
        file_size=102400,
        depth_from=0.0,
        depth_to=3000.0,
        sample_count=1000,
        project_id=test_project.id,
        status="processing"
    )
    test_db.add(log)
    test_db.commit()
    test_db.refresh(log)
    return log


@pytest.fixture
def test_curve_data(test_db, test_well_log):
    """创建测试曲线数据"""
    curves = []
    for depth in range(0, 100, 10):
        curve = CurveData(
            log_id=test_well_log.id,
            depth=float(depth),
            curve_name="GR",
            value=50.0 + depth * 0.1
        )
        curves.append(curve)
    
    test_db.add_all(curves)
    test_db.commit()
    
    for curve in curves:
        test_db.refresh(curve)
    
    return curves


@pytest.fixture
def test_ai_model(test_db):
    """创建测试 AI 模律"""
    model = AIModel(
        name="Test Model",
        version="1.0.0",
        description="A test AI model",
        model_type="regression",
        accuracy=0.95,
        status="active"
    )
    test_db.add(model)
    test_db.commit()
    test_db.refresh(model)
    return model


@pytest.fixture
def test_prediction(test_db, test_well_log, test_ai_model):
    """创建测试预测"""
    prediction = Prediction(
        log_id=test_well_log.id,
        model_id=test_ai_model.id,
        results_json={"prediction": [1, 2, 3]},
        confidence=0.92,
        execution_time=5.2,
        status="success"
    )
    test_db.add(prediction)
    test_db.commit()
    test_db.refresh(prediction)
    return prediction


# ==================== 认证 Fixtures ====================

@pytest.fixture
def access_token(test_user):
    """生成用户访问令牌"""
    from app.core.security import SecurityUtility
    token = SecurityUtility.create_access_token(
        data={"sub": test_user.username}
    )
    return token


@pytest.fixture
def admin_token(admin_user):
    """生成管理员访问令牌"""
    from app.core.security import SecurityUtility
    token = SecurityUtility.create_access_token(
        data={"sub": admin_user.username}
    )
    return token


@pytest.fixture
def auth_headers(access_token):
    """认证请求头"""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def admin_headers(admin_token):
    """管理员认证请求头"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


# ==================== 工具函数 ====================

@pytest.fixture
def assert_valid_response():
    """验证 API 响应格式"""
    def _assert(response_data):
        assert isinstance(response_data, dict)
        if response_data.get("success"):
            assert response_data.get("message") is not None
            # success=True 时通常包含数据
        else:
            assert response_data.get("error") is not None
            assert response_data.get("message") is not None
    
    return _assert


@pytest.fixture
def assert_pagination():
    """验证分页响应"""
    def _assert(response_data):
        assert "data" in response_data
        assert "total" in response_data
        assert "skip" in response_data
        assert "limit" in response_data
        assert isinstance(response_data["data"], list)
        assert isinstance(response_data["total"], int)
    
    return _assert
