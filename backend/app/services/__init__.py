"""应用服务层初始化

业务逻辑服务层提供高级业务操作，整合CRUD层和业务规则。
每个服务包含特定领域的业务逻辑和工作流程。

服务设计原则:
1. 单一职责: 每个服务负责一个业务领域
2. 一致的错误处理: 返回Dict[str, Any]，包含success/error/message
3. 审计日志: 记录所有重要操作
4. 业务规则验证: 在数据库操作前进行验证
5. 与CRUD层解耦: 业务逻辑独立于数据库实现

服务列表:
- UserService: 用户管理和认证
- ProjectService: 项目生命周期管理
- DataService: 测井数据管理和分析
- PredictionService: AI预测结果管理
- FileParserService: 多格式文件解析
"""

from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.data_service import DataService
from app.services.prediction_service import PredictionService
from app.services.file_parser_service import FileParserService

__all__ = [
    "UserService",
    "ProjectService",
    "DataService",
    "PredictionService",
    "FileParserService",
]


class ServiceFactory:
    """服务工厂类 - 提供统一的服务访问接口"""
    
    @staticmethod
    def get_user_service():
        """获取用户服务"""
        return UserService
    
    @staticmethod
    def get_project_service():
        """获取项目服务"""
        return ProjectService
    
    @staticmethod
    def get_data_service():
        """获取数据服务"""
        return DataService
    
    @staticmethod
    def get_prediction_service():
        """获取预测服务"""
        return PredictionService
    
    @staticmethod
    def get_file_parser_service():
        """获取文件解析服务"""
        return FileParserService


# 快速访问
__all__.extend(["ServiceFactory"])
