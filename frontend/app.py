import os
import streamlit as st
import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = f"http://localhost:{os.getenv('APP_PORT', '8000')}/api"

if "uploaded" not in st.session_state:
    st.session_state["uploaded"] = False

st.set_page_config(
    page_title="RAG 知识库问答系统",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG 知识库问答系统")

tab1, tab2 = st.tabs(["问答", "文档管理"])

with tab1:
    st.subheader("向知识库提问")
    
    query = st.text_input("输入您的问题:", placeholder="请输入您想查询的问题...")
    
    top_k = st.slider("返回相关文档数量:", min_value=1, max_value=10, value=5)
    
    if st.button("提交查询", type="primary"):
        if query.strip():
            with st.spinner("正在检索和生成答案..."):
                try:
                    response = httpx.post(
                        f"{API_URL}/query",
                        json={"query": query, "top_k": top_k},
                        timeout=120.0
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    st.success("查询完成!")
                    st.markdown("### 回答")
                    st.write(data["answer"])
                    
                    if data["sources"]:
                        st.markdown("### 参考来源")
                        for source in data["sources"]:
                            st.info(f"📄 **{source['filename']}** (相似度: {source['similarity']:.2%})")
                except Exception as e:
                    st.error(f"查询失败: {str(e)}")
        else:
            st.warning("请输入问题")

with tab2:
    st.subheader("文档管理")
    
    uploaded_file = st.file_uploader("上传文档", type=["pdf", "md", "json", "txt", "docx", "xlsx"])
    
    if uploaded_file is not None and not st.session_state["uploaded"]:
        with st.spinner("正在上传和处理文档..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = httpx.post(f"{API_URL}/upload", files=files, timeout=60.0)
                response.raise_for_status()
                st.success(f"文档 '{uploaded_file.name}' 上传成功!")
                st.session_state["uploaded"] = True
                st.rerun()
            except Exception as e:
                st.error(f"上传失败: {str(e)}")
    
    st.markdown("---")
    st.subheader("已上传的文档")
    
    try:
        response = httpx.get(f"{API_URL}/documents", timeout=10.0)
        response.raise_for_status()
        docs = response.json().get("documents", [])
        
        if docs:
            for doc in docs:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"📄 {doc['filename']}")
                col2.write(f"类型: {doc['file_type']}")
                if col3.button("删除", key=f"delete_{doc['id']}"):
                    try:
                        delete_response = httpx.delete(f"{API_URL}/documents/{doc['id']}", timeout=10.0)
                        delete_response.raise_for_status()
                        st.success("文档已删除")
                        st.rerun()
                    except Exception as e:
                        st.error(f"删除失败: {str(e)}")
        else:
            st.info("暂无文档，请先上传文档")
    except Exception as e:
        st.error(f"获取文档列表失败: {str(e)}")

st.sidebar.title("关于")
st.sidebar.info("""
这是一个基于 RAG (Retrieval-Augmented Generation) 的知识库问答系统。

**功能特点:**
- 支持多种文档格式上传
- 基于向量检索的智能问答
- 阿里云百炼大语言模型支持
""")