"""
日志工具模块
使用loguru提供统一的日志记录功能
"""
from loguru import logger
import sys
from pathlib import Path
from src.config import settings


def setup_logger():
    """配置日志系统"""
    # 移除默认的handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # 添加文件输出
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="100 MB",  # 日志文件大小达到100MB时轮转
        retention="30 days",  # 保留30天的日志
        compression="zip",  # 压缩旧日志
        encoding="utf-8"
    )
    
    logger.info("日志系统初始化完成")
    return logger


# 初始化日志
setup_logger()


def get_logger():
    """获取logger实例"""
    return logger


if __name__ == "__main__":
    # 测试日志功能
    logger.debug("这是一条调试信息")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    logger.success("这是一条成功信息")
