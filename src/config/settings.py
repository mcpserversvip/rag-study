"""
配置管理模块
加载和管理系统配置,包括API密钥、数据库连接等
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from dotenv import load_dotenv

# 加载.env文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class Settings(BaseSettings):
    """系统配置类"""
    
    # 阿里云DashScope配置
    dashscope_api_key: str = Field(default="", env="DASHSCOPE_API_KEY")
    
    # MySQL数据库配置
    mysql_host: str = Field(default="localhost", env="MYSQL_HOST")
    mysql_port: int = Field(default=3306, env="MYSQL_PORT")
    mysql_user: str = Field(default="medical_user", env="MYSQL_USER")
    mysql_password: str = Field(default="medical_password_2024", env="MYSQL_PASSWORD")
    mysql_database: str = Field(default="medical_knowledge_base", env="MYSQL_DATABASE")
    
    # Flask应用配置
    flask_host: str = Field(default="0.0.0.0", env="FLASK_HOST")
    flask_port: int = Field(default=5000, env="FLASK_PORT")
    flask_debug: bool = Field(default=True, env="FLASK_DEBUG")
    
    # RAG配置
    embedding_model: str = Field(default="text-embedding-v2", env="EMBEDDING_MODEL")
    llm_model: str = Field(default="qwen-plus-2025-07-28", env="LLM_MODEL")
    multimodal_model: str = Field(default="qwen-vl-plus", env="MULTIMODAL_MODEL")
    knowledge_base_path: str = Field(default="./knowledge_base/medical", env="KNOWLEDGE_BASE_PATH")
    
    # 智能体配置
    agent_model: str = Field(default="qwen-plus-latest", env="AGENT_MODEL")
    agent_max_iterations: int = Field(default=10, env="AGENT_MAX_ITERATIONS")
    
    # 安全配置
    enable_safety_check: bool = Field(default=True, env="ENABLE_SAFETY_CHECK")
    enable_ethics_check: bool = Field(default=True, env="ENABLE_ETHICS_CHECK")
    enable_humanistic_care: bool = Field(default=True, env="ENABLE_HUMANISTIC_CARE")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/medical_assistant.log", env="LOG_FILE")
    
    @property
    def mysql_url(self) -> str:
        """获取MySQL连接URL"""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"

    @computed_field
    @property
    def project_root(self) -> Path:
        """获取项目根目录"""
        return Path(__file__).parent.parent.parent
    
    def validate_api_key(self) -> bool:
        """验证API密钥是否配置"""
        if not self.dashscope_api_key or self.dashscope_api_key == "your-dashscope-api-key-here":
            return False
        return True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略额外字段


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def init_environment():
    """初始化环境变量"""
    # 设置阿里云API密钥
    if settings.dashscope_api_key:
        os.environ['DASHSCOPE_API_KEY'] = settings.dashscope_api_key
    
    # 创建必要的目录
    Path(settings.knowledge_base_path).mkdir(parents=True, exist_ok=True)
    Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # 测试配置加载
    print("配置信息:")
    print(f"  API Key配置: {'✅' if settings.validate_api_key() else '❌ 未配置'}")
    print(f"  MySQL URL: {settings.mysql_url}")
    print(f"  知识库路径: {settings.knowledge_base_path}")
    print(f"  LLM模型: {settings.llm_model}")
    print(f"  多模态模型: {settings.multimodal_model}")
    print(f"  安全检查: {'启用' if settings.enable_safety_check else '禁用'}")
    print(f"  伦理检查: {'启用' if settings.enable_ethics_check else '禁用'}")
    print(f"  人文关怀: {'启用' if settings.enable_humanistic_care else '禁用'}")
