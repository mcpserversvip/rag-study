#!/bin/bash

# 糖尿病诊断医疗助手 - 环境搭建脚本
# 使用uv管理Python 3.12环境

set -e

echo "========================================="
echo "糖尿病诊断医疗助手 - 环境搭建"
echo "========================================="

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv未安装,正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✅ uv已安装"
fi

# 创建Python 3.12虚拟环境
echo ""
echo "📦 创建Python 3.12虚拟环境..."
uv venv --python 3.12

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo ""
echo "📥 安装项目依赖..."
uv pip install -r requirements.txt

# 创建必要的目录结构
echo ""
echo "📁 创建项目目录结构..."
mkdir -p src/{api,agent,rag,database,pdf_parser,config,utils,templates,static}
mkdir -p scripts
mkdir -p tests/{unit,integration}
mkdir -p knowledge_base/medical
mkdir -p logs

# 检查.env文件
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env文件不存在,从.env.example复制..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件,填入您的API密钥和配置"
fi

# 检查Docker
echo ""
if command -v docker &> /dev/null; then
    echo "✅ Docker已安装"
    
    # 启动MySQL容器
    echo "🐳 启动MySQL容器..."
    docker-compose up -d
    
    echo "⏳ 等待MySQL启动..."
    sleep 10
    
    echo "✅ MySQL容器已启动"
else
    echo "❌ Docker未安装,请先安装Docker"
    echo "   macOS: brew install --cask docker"
fi

echo ""
echo "========================================="
echo "✅ 环境搭建完成!"
echo "========================================="
echo ""
echo "下一步操作:"
echo "1. 编辑.env文件,填入您的DASHSCOPE_API_KEY"
echo "2. 运行数据库初始化: uv run python scripts/init_database.py"
echo "3. 构建知识库: uv run python scripts/build_knowledge_base.py"
echo "4. 启动应用: uv run python src/app.py"
echo ""
echo "激活虚拟环境: source .venv/bin/activate"
echo "========================================="
