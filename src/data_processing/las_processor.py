import lasio
import pandas as pd
import numpy as np
from typing import List, Dict

class WellLogProcessor:
    """测井数据处理类"""
    
    def __init__(self, file_path: str):
        self.las = lasio.read(file_path)
        self.df = self.las.df()
    
    def get_curves(self) -> List[str]:
        """获取所有曲线名称"""
        return self.df.columns.tolist()
    
    def normalize_data(self, method='minmax'):
        """数据归一化"""
        if method == 'minmax':
            return (self.df - self.df.min()) / (self.df.max() - self.df.min())
        elif method == 'zscore':
            return (self.df - self.df.mean()) / self.df.std()
    
    def fill_missing(self, method='interpolate'):
        """填充缺失值"""
        if method == 'interpolate':
            return self.df.interpolate(method='linear')
        elif method == 'forward':
            return self.df.fillna(method='ffill')
    
    def extract_features(self) -> pd.DataFrame:
        """提取特征"""
        features = pd.DataFrame()
        
        # 基础统计特征
        for col in self.df.columns:
            features[f'{col}_mean'] = [self.df[col].mean()]
            features[f'{col}_std'] = [self.df[col].std()]
            features[f'{col}_max'] = [self.df[col].max()]
            features[f'{col}_min'] = [self.df[col].min()]
        
        return features