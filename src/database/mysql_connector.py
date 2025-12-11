"""
MySQL数据库连接器
提供数据库连接和基础操作
"""
from typing import Optional, Dict, List, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import pymysql

from src.config import settings
from src.utils.logger import logger


class MySQLConnector:
    """MySQL数据库连接器"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.engine = None
        self.SessionLocal = None
        self._init_engine()
    
    def _init_engine(self):
        """初始化数据库引擎"""
        try:
            # 创建数据库引擎
            self.engine = create_engine(
                settings.mysql_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # 连接前检查连接是否有效
                pool_recycle=3600,  # 1小时后回收连接
                echo=False  # 不打印SQL语句
            )
            
            # 创建Session工厂
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"数据库连接成功: {settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}")
            
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """获取数据库会话(上下文管理器)"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        执行查询语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                # 将结果转换为字典列表
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"查询执行失败: {query}, 错误: {e}")
            raise
    
    def execute_update(self, query: str, params: Optional[Dict] = None) -> int:
        """
        执行更新语句(INSERT/UPDATE/DELETE)
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            影响的行数
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                conn.commit()
                return result.rowcount
        except Exception as e:
            logger.error(f"更新执行失败: {query}, 错误: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            result = self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except Exception:
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")


# 全局数据库连接器实例
db_connector = MySQLConnector()


def get_db_connector() -> MySQLConnector:
    """获取数据库连接器实例"""
    return db_connector


if __name__ == "__main__":
    # 测试数据库连接
    connector = get_db_connector()
    
    if connector.test_connection():
        logger.success("✅ 数据库连接测试成功")
        
        # 测试查询
        result = connector.execute_query("SELECT COUNT(*) as count FROM patient_info")
        logger.info(f"患者信息表记录数: {result[0]['count']}")
    else:
        logger.error("❌ 数据库连接测试失败")
