"""CRUD操作层初始化"""

from app.crud.user import UserCRUD
from app.crud.project import ProjectCRUD
from app.crud.data import WellLogCRUD, CurveDataCRUD
from app.crud.model import AIModelCRUD
from app.crud.prediction import PredictionCRUD

__all__ = [
    "UserCRUD",
    "ProjectCRUD",
    "WellLogCRUD",
    "CurveDataCRUD",
    "AIModelCRUD",
    "PredictionCRUD",
]
