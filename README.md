# 糖尿病诊断医疗助手

基于RAG和智能体技术的专业医疗决策支持系统

## 项目简介

本项目是一个专家级医疗决策支持智能体系统,整合多模态RAG技术和智能体技术,为糖尿病和高血压诊疗提供全流程决策支持。

### 核心特性

- **多模态PDF解析**: 使用阿里云多模态模型(qwen-vl-plus)解析医疗指南PDF中的图文内容
- **RAG知识库**: 基于LlamaIndex构建向量索引,整合医疗指南知识
- **MySQL数据库集成**: 整合患者信息、病历、检验结果、用药记录等医疗数据
- **智能决策引擎**: 提供个性化诊疗建议和风险评估
- **安全风险控制**: 内置医学伦理检查、用药安全校验和人文关怀机制
- **Web界面**: 基于Flask的流式对话界面

### 技术栈

- **Python**: 3.12 (使用uv管理)
- **Web框架**: Flask + Flask-CORS
- **RAG框架**: LlamaIndex
- **数据库**: MySQL 8.0 (Docker部署)
- **多模态模型**: 阿里云通义千问 qwen-vl-plus
- **LLM模型**: 阿里云通义千问 qwen-plus
- **Embedding**: DashScope text-embedding-v2

## 快速开始

### 1. 环境搭建

```bash
# 运行环境搭建脚本
./setup.sh
```

这将自动完成:
- 安装uv(如果未安装)
- 创建Python 3.12虚拟环境
- 安装项目依赖
- 启动MySQL Docker容器
- 创建必要的目录结构

### 2. 配置API密钥

编辑`.env`文件,填入您的阿里云DashScope API密钥:

```bash
DASHSCOPE_API_KEY=your-api-key-here
```

获取API密钥: https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key

### 3. 初始化数据库

```bash
# 激活虚拟环境
source .venv/bin/activate

# 初始化数据库(执行DDL并导入CSV数据)
uv run python scripts/init_database.py
```

### 4. 构建知识库

```bash
# 解析PDF文档并构建RAG向量索引
uv run python scripts/build_knowledge_base.py
```

⚠️ 注意: PDF解析会调用阿里云多模态API,可能需要较长时间和产生API费用。解析结果会缓存,避免重复调用。

### 5. 启动应用

```bash
# 启动Flask Web应用
uv run python src/app.py
```

访问 http://localhost:5000 使用医疗助手

## 项目结构

```
rag-study/
├── data/                           # 原始数据
│   ├── 高血压诊疗指南.pdf
│   ├── 中国高血压防治指南.pdf
│   └── 糖尿病病例统计.xlsx
├── db/                             # 数据库相关
│   ├── ddl.sql                     # 数据库表结构
│   └── data-csv/                   # CSV数据文件
├── src/                            # 源代码
│   ├── app.py                      # Flask主应用
│   ├── agent/                      # 智能体模块
│   │   ├── safety_checker.py      # 安全检查器
│   │   └── tools.py                # 医疗工具集
│   ├── rag/                        # RAG模块
│   │   ├── knowledge_builder.py   # 知识库构建
│   │   ├── query_engine.py        # 查询引擎
│   │   └── prompt_templates.py    # Prompt模板
│   ├── database/                   # 数据库模块
│   │   ├── mysql_connector.py     # MySQL连接器
│   │   └── medical_data_retriever.py  # 医疗数据检索
│   ├── pdf_parser/                 # PDF解析模块
│   │   └── multimodal_parser.py   # 多模态解析器
│   ├── config/                     # 配置模块
│   │   └── settings.py             # 配置管理
│   ├── utils/                      # 工具模块
│   │   └── logger.py               # 日志工具
│   └── templates/                  # Web模板
│       └── index.html              # 前端界面
├── scripts/                        # 脚本
│   ├── init_database.py            # 数据库初始化
│   └── build_knowledge_base.py    # 知识库构建
├── knowledge_base/                 # 知识库存储
├── logs/                           # 日志文件
├── temp/                           # 临时文件
├── docker-compose.yml              # Docker配置
├── setup.sh                        # 环境搭建脚本
├── requirements.txt                # Python依赖
├── .env.example                    # 环境变量模板
└── README.md                       # 项目文档
```

## API接口

### 健康检查
```
GET /api/health
```

### 对话接口
```
POST /api/chat
Content-Type: application/json

{
  "question": "糖尿病的诊断标准是什么?",
  "patient_id": "1001_0_20210730",  // 可选
  "enable_safety_check": true
}
```

### 患者信息查询
```
GET /api/patient/{patient_id}
```

### 患者综合数据
```
GET /api/patient/{patient_id}/comprehensive
```

### 糖尿病风险评估
```
GET /api/assessment/diabetes/{patient_id}
```

### 用药安全检查
```
POST /api/safety/medication
Content-Type: application/json

{
  "patient_id": "1001_0_20210730",
  "medication": "二甲双胍"
}
```

## 安全特性

### 1. 医学伦理检查
- 检测过度承诺疗效的表述
- 避免使用"保证治愈"等禁忌词
- 确保尊重患者自主权

### 2. 用药安全校验
- 检查药物相互作用
- 验证剂量合理性
- 识别禁忌症

### 3. 高风险预警
- 自动检测高风险操作(停药、换药等)
- 添加明确的风险提示
- 强调需咨询医生

### 4. 人文关怀
- 使用温和、专业的语言
- 关注患者心理状态
- 提供鼓励和支持

### 5. 免责声明
- 所有建议自动添加免责声明
- 明确系统仅供参考
- 强调需医生指导

## 数据库表结构

- `patient_info`: 患者基本信息
- `medical_records`: 患者病历记录
- `lab_results`: 检查检验结果
- `medication_records`: 用药记录
- `diagnosis_records`: 诊断记录
- `hypertension_risk_assessment`: 高血压风险评估
- `diabetes_control_assessment`: 糖尿病控制评估
- `guideline_recommendations`: 指南推荐规则
- `system_logs`: 系统日志

## 开发指南

### 运行测试

```bash
# 运行单元测试
uv run pytest tests/unit/ -v

# 运行集成测试
uv run pytest tests/integration/ -v
```

### 查看日志

日志文件位于 `logs/medical_assistant.log`

### 停止MySQL容器

```bash
docker-compose down
```

### 重新构建知识库

```bash
# 删除现有知识库
rm -rf knowledge_base/medical

# 重新构建
uv run python scripts/build_knowledge_base.py
```

## 注意事项

1. **API费用**: PDF解析和LLM调用会产生阿里云API费用,请注意控制使用量
2. **缓存机制**: PDF解析结果会缓存在`temp/parsed_pdfs`目录,避免重复调用
3. **数据安全**: 本系统处理医疗数据,请确保符合相关法规要求
4. **仅供参考**: 系统建议仅供医疗专业人员参考,不能替代医生诊断

## 许可证

Apache License 2.0

## 联系方式

如有问题或建议,请提交Issue。
