import torch
import torch.nn as nn
from transformers import PreTrainedModel, PretrainedConfig

class LogTransformerConfig(PretrainedConfig):
    model_type = "log_transformer"
    
    def __init__(
        self,
        vocab_size=1000,
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        max_position_embeddings=512,
        num_curves=10,  # 测井曲线数量
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.max_position_embeddings = max_position_embeddings
        self.num_curves = num_curves

class LogTransformer(PreTrainedModel):
    config_class = LogTransformerConfig
    
    def __init__(self, config):
        super().__init__(config)
        
        # 输入嵌入层
        self.curve_embedding = nn.Linear(config.num_curves, config.hidden_size)
        self.position_embedding = nn.Embedding(
            config.max_position_embeddings, 
            config.hidden_size
        )
        
        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.hidden_size,
            nhead=config.num_attention_heads,
            dim_feedforward=config.intermediate_size,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer, 
            num_layers=config.num_hidden_layers
        )
        
        # 输出层
        self.output_layer = nn.Linear(config.hidden_size, config.num_curves)
        
    def forward(self, x, attention_mask=None):
        # x: (batch_size, seq_len, num_curves)
        batch_size, seq_len, _ = x.shape
        
        # 嵌入
        x = self.curve_embedding(x)
        
        # 位置编码
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)
        x = x + self.position_embedding(positions)
        
        # Transformer编码
        x = self.transformer(x, src_key_padding_mask=attention_mask)
        
        # 输出预测
        output = self.output_layer(x)
        
        return output