from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict


class ServerConfig(BaseSettings):
    url: str
    username: str
    password: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        # 你还可以添加从 YAML 加载的逻辑
    )

    servers: Dict[str, ServerConfig]
    firecrawl_api_key: str
    ollama_model: str = "qwen3:latest"


# 在项目入口处加载
try:
    settings = Settings()
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    exit(1)

# 在其他模块中，直接 from erp_core.config import settings 来使用