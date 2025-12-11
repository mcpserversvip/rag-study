# 项目背景

## 目标
糖尿病诊断医疗助手 - 基于RAG和智能体技术的专业医疗决策支持系统。整合多模态RAG技术和智能体技术,为糖尿病和高血压诊疗提供全流程决策支持。

### 核心目标
- 多模态PDF解析：使用阿里云多模态模型解析医疗指南PDF中的图文内容
- RAG知识库：基于LlamaIndex构建向量索引,整合医疗指南知识
- 智能决策引擎：提供个性化诊疗建议和风险评估
- 安全风险控制：内置医学伦理检查、用药安全校验和人文关怀机制

## 技术栈

### 核心语言与工具
- **Python**: 3.12 (使用 `uv` 管理虚拟环境)
- **包管理**: `uv` + `requirements.txt`

### Web框架
- **Flask**: 3.0.0 (主应用框架)
- **Flask-CORS**: 4.0.0 (跨域支持)

### RAG与向量索引
- **LlamaIndex**: >=0.10.0 (核心RAG框架)
- **llama-index-embeddings-dashscope**: 阿里云DashScope Embedding
- **llama-index-llms-dashscope**: 阿里云通义千问LLM
- **llama-index-llms-openai-like**: OpenAI兼容接口

### 数据库
- **MySQL**: 8.0 (Docker部署,docker-compose.yml配置)
- **pymysql**: 1.1.0
- **sqlalchemy**: 2.0.23

### AI模型 (阿里云DashScope)
- **多模态模型**: qwen-vl-plus (PDF图像解析)
- **LLM模型**: qwen-plus (对话与推理)
- **Embedding**: text-embedding-v2 (向量嵌入)

### PDF处理
- **pypdf**: 3.17.4
- **pdf2image**: 1.17.0
- **pillow**: 10.1.0

### 其他依赖
- **python-dotenv**: 环境变量管理
- **pydantic/pydantic-settings**: 配置管理
- **loguru**: 日志
- **pandas/openpyxl**: 数据处理
- **pytest**: 测试框架

## 项目规范

### 代码风格
- **语言**: Python代码,中文注释和文档
- **Docstring风格**: Google style docstrings (Args/Returns/Raises)
- **命名规范**:
  - 类名: `PascalCase` (如 `KnowledgeBuilder`, `MedicalDataRetriever`)
  - 函数/变量: `snake_case` (如 `load_index`, `persist_dir`)
  - 常量: `UPPER_SNAKE_CASE`
- **类型提示**: 使用 `typing` 模块进行类型标注 (如 `List[Document]`, `Optional[str]`)
- **日志**: 使用 `loguru` 的 `logger` 实例,通过 `src/utils/logger.py` 统一管理

### 架构模式
- **模块化架构**: 按功能划分模块
  - `src/agent/`: 智能体模块 (安全检查、工具集)
  - `src/rag/`: RAG模块 (知识库构建、查询引擎、Prompt模板)
  - `src/database/`: 数据库模块 (MySQL连接器、医疗数据检索)
  - `src/pdf_parser/`: PDF解析模块 (多模态解析器)
  - `src/config/`: 配置模块 (settings管理)
  - `src/utils/`: 工具模块 (日志等)
- **单例模式**: 通过 `get_xxx()` 函数获取模块实例
- **配置管理**: 使用 `pydantic-settings` 的 `Settings` 类管理配置,从 `.env` 文件加载

### 文件组织
```
src/
├── app.py                      # Flask主应用入口
├── agent/                      # 智能体模块
├── rag/                        # RAG模块
├── database/                   # 数据库模块
├── pdf_parser/                 # PDF解析模块
├── config/                     # 配置模块
├── utils/                      # 工具模块
└── templates/                  # Web模板

scripts/                        # 初始化/构建脚本
├── init_database.py           # 数据库初始化
├── build_knowledge_base.py    # 知识库构建

db/                            # 数据库相关
├── ddl.sql                    # 表结构定义
└── data-csv/                  # CSV数据文件

data/                          # 原始数据 (PDF指南等)
knowledge_base/                # RAG向量索引持久化目录
```

### 测试策略
- **测试框架**: pytest
- **测试目录**: `tests/unit/` (单元测试), `tests/integration/` (集成测试)
- **运行命令**:
  - `uv run pytest tests/unit/ -v`
  - `uv run pytest tests/integration/ -v`

### Git 工作流
- **分支策略**: 功能分支开发,合并到主分支
- **提交规范**: 建议使用语义化提交信息 (feat/fix/docs/refactor)

## 领域背景

### 医疗场景
- **目标疾病**: 糖尿病、高血压
- **数据来源**: 
  - 医疗指南PDF文档 (高血压诊疗指南、中国高血压防治指南)
  - 患者医疗数据 (MySQL数据库存储)

### 数据库表结构
- `patient_info`: 患者基本信息
- `medical_records`: 患者病历记录
- `lab_results`: 检查检验结果
- `medication_records`: 用药记录
- `diagnosis_records`: 诊断记录
- `hypertension_risk_assessment`: 高血压风险评估
- `diabetes_control_assessment`: 糖尿病控制评估
- `guideline_recommendations`: 指南推荐规则
- `system_logs`: 系统日志

### 安全机制
- **医学伦理检查**: 检测过度承诺疗效的表述
- **用药安全校验**: 检查药物相互作用、剂量合理性、禁忌症
- **高风险预警**: 自动检测高风险操作(停药、换药等)
- **人文关怀**: 使用温和、专业的语言
- **免责声明**: 所有建议自动添加免责声明

## 重要约束

### 技术约束
- **Python版本**: 必须使用 Python 3.12
- **环境管理**: 使用 `uv` 而非 pip/conda
- **数据库**: MySQL通过Docker运行,不支持其他数据库

### 业务约束
- **医疗合规**: 系统建议仅供医疗专业人员参考,不能替代医生诊断
- **API费用**: PDF解析和LLM调用会产生阿里云API费用,需注意控制使用量
- **数据安全**: 处理医疗数据,需符合相关法规要求

### 缓存机制
- PDF解析结果缓存在 `temp/parsed_pdfs` 目录,避免重复API调用

## 外部依赖

### 阿里云DashScope
- **用途**: 多模态模型、LLM模型、Embedding模型
- **配置**: `DASHSCOPE_API_KEY` 环境变量
- **文档**: https://help.aliyun.com/zh/model-studio/

### MySQL Docker
- **配置文件**: `docker-compose.yml`
- **默认端口**: 3306
- **默认用户**: medical_user
- **默认数据库**: medical_knowledge_base

### 启动命令
```bash
# 1. 环境搭建
./setup.sh

# 2. 配置API密钥
# 编辑 .env 文件

# 3. 初始化数据库
uv run python scripts/init_database.py

# 4. 构建知识库
uv run python scripts/build_knowledge_base.py

# 5. 启动应用
uv run python src/app.py
```
