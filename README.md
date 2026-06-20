# 📚 RAG 知识库问答系统

一个基于 Retrieval-Augmented Generation (RAG) 的个人知识库问答系统，支持多种文档格式，使用阿里云百炼平台大模型进行智能问答。

## ✨ 功能特点

- **多模态文档支持**: 支持 PDF、Markdown、JSON、Word、Excel、TXT 等多种文档格式
- **智能问答**: 基于大模型的问答能力，结合知识库内容进行精准回答
- **向量检索**: 使用 PostgreSQL + pgvector 进行高效的向量相似性检索
- **Web 界面**: 简洁易用的 Streamlit 前端界面
- **Docker 部署**: 支持 Docker Compose 一键部署

## 🛠️ 技术栈

- **后端框架**: FastAPI
- **前端框架**: Streamlit
- **向量数据库**: PostgreSQL + pgvector
- **大模型**: 阿里云百炼平台 (Qwen)
- **文档处理**: pdfplumber, python-docx, pandas
- **向量嵌入**: 阿里云百炼 Embedding

## 📁 项目结构

```
RAG_system/
├── backend/
│   ├── src/
│   │   ├── main.py          # FastAPI 主入口
│   │   ├── document_loader.py  # 文档加载解析模块
│   │   ├── vector_store.py     # 向量存储检索模块
│   │   └── llm_integrator.py   # LLM 集成模块
│   └── config/
│       └── init_db.py       # 数据库初始化脚本
├── frontend/
│   └── app.py               # Streamlit 前端应用
├── data/                    # 临时文件存储目录
├── .env                     # 环境配置文件
├── .gitignore               # Git 忽略配置
├── docker-compose.yml       # 数据库 Docker 配置
├── docker-compose.full.yml  # 完整服务 Docker 配置
├── Dockerfile.backend       # 后端 Dockerfile
├── Dockerfile.frontend      # 前端 Dockerfile
├── requirements.txt         # Python 依赖
└── README.md               # 项目说明文档
```

## 🚀 快速开始

### 前提条件

- Docker 和 Docker Compose 已安装
- 阿里云百炼平台 API Key (需要在阿里云控制台申请)

### 1. 配置环境变量

编辑 `.env` 文件，填入你的阿里云百炼平台 API Key：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

### 2. 使用 Docker Compose 部署

**方式一：仅启动数据库（适合开发调试）**

```bash
docker-compose up -d
```

然后在本地运行后端和前端：

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python backend/config/init_db.py

# 运行后端服务
cd backend/src
python main.py

# 运行前端服务（新开终端）
cd frontend
streamlit run app.py
```

**方式二：启动完整服务（推荐）**

```bash
docker-compose -f docker-compose.full.yml up -d
```

### 3. 访问应用

- 前端页面: http://localhost:8501
- API 接口: http://localhost:8000

## 📖 使用说明

### 上传文档

1. 打开前端页面 http://localhost:8501
2. 切换到「文档管理」标签页
3. 点击「上传文档」按钮
4. 选择支持的文档格式（PDF、MD、JSON、TXT、DOCX、XLSX）

### 提问

1. 切换到「问答」标签页
2. 在输入框中输入你的问题
3. 点击「提交查询」按钮
4. 系统会返回答案和相关参考文档

## 🔧 API 接口

### 上传文档

```
POST /api/upload
Content-Type: multipart/form-data

参数:
- file: 文件 (支持 pdf, md, json, txt, docx, xlsx)
```

### 问答查询

```
POST /api/query
Content-Type: application/json

{
  "query": "你的问题",
  "top_k": 5
}
```

### 文档列表

```
GET /api/documents
```

### 删除文档

```
DELETE /api/documents/{doc_id}
```

## 📝 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| POSTGRES_HOST | 数据库主机 | localhost |
| POSTGRES_PORT | 数据库端口 | 5432 |
| POSTGRES_USER | 数据库用户名 | rag_user |
| POSTGRES_PASSWORD | 数据库密码 | rag_password |
| POSTGRES_DB | 数据库名称 | rag_db |
| DASHSCOPE_API_KEY | 阿里云百炼 API Key | - |
| DASHSCOPE_MODEL_NAME | 大模型名称 | qwen-plus |
| EMBEDDING_MODEL | 嵌入模型名称 | text-embedding-v1 |
| APP_HOST | 应用主机 | 0.0.0.0 |
| APP_PORT | 应用端口 | 8000 |
| FRONTEND_PORT | 前端端口 | 8501 |
| TOP_K | 默认返回文档数 | 5 |

## 📄 支持的文档格式

- PDF (.pdf)
- Markdown (.md)
- JSON (.json)
- Plain Text (.txt)
- Microsoft Word (.docx)
- Microsoft Excel (.xlsx)

## 📜 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！