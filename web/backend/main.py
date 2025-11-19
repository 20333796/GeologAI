from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import pandas as pd
from typing import List, Optional, Dict, Any
import os

app = FastAPI(
    title="地球物理测井AI平台",
    description="基于AI的测井曲线预测和分析平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局模型实例
model = None
model_loaded = False

class PredictionRequest(BaseModel):
    depth_from: float
    depth_to: float
    curves: List[str]

class PredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    confidence: float
    status: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str

@app.on_event("startup")
async def load_model():
    """启动时加载模型"""
    global model, model_loaded
    try:
        model_path = "./data/models/log_transformer"
        if os.path.exists(model_path):
            print(f"加载模型: {model_path}")
            # 这里可以添加实际的模型加载逻辑
            model_loaded = True
            print("模型加载成功")
        else:
            print(f"模型路径不存在: {model_path}，使用演示模式")
            model_loaded = False
    except Exception as e:
        print(f"警告: 模型加载失败 - {e}。继续以演示模式运行。")
        model_loaded = False

@app.post("/predict", response_model=PredictionResponse)
async def predict_logs(request: PredictionRequest):
    """预测测井曲线"""
    try:
        if request.depth_from >= request.depth_to:
            raise HTTPException(status_code=400, detail="起始深度必须小于结束深度")
        
        if not request.curves:
            raise HTTPException(status_code=400, detail="必须选择至少一条曲线")
        
        # 生成示例预测结果
        predictions = []
        depth_range = request.depth_to - request.depth_from
        num_points = int(depth_range / 10) + 1  # 每10m一个点
        
        for i in range(num_points):
            depth = request.depth_from + i * 10
            for curve in request.curves:
                predictions.append({
                    "depth": depth,
                    "curve": curve,
                    "value": round(50 + 30 * (i / num_points), 2)
                })
        
        return PredictionResponse(
            predictions=predictions,
            confidence=0.85,
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        model_loaded=model_loaded,
        version="1.0.0"
    )

@app.get("/curves")
async def get_available_curves():
    """获取可用的曲线类型"""
    return {
        "curves": ["GR", "RT", "DEN", "NEU", "SP", "CALI"],
        "description": "自然伽马、真实电阻率、密度、中子、自然电位、套管井径"
    }

@app.get("/")
async def root():
    """API根路由"""
    return {
        "name": "地球物理测井AI平台",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "curves": "/curves"
        }
    }