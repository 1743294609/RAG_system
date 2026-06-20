import os
import dashscope
from dashscope import Generation
from dotenv import load_dotenv

load_dotenv()

class LLMIntegrator:
    def __init__(self):
        self.model_name = os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus")
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY is not set in environment variables")
        
        dashscope.api_key = self.api_key
    
    def generate_response(self, query, context):
        system_prompt = """你是一个专业的知识库问答助手。请根据提供的参考文档内容回答用户的问题。
        
规则：
1. 只使用提供的参考文档内容进行回答
2. 如果参考文档中没有相关信息，请明确说明"根据提供的文档，我无法回答这个问题"
3. 回答要简洁明了，用自然友好的语言
4. 如果问题与文档内容相关，请尽量详细回答"""
        
        context_str = "\n\n".join([f"文档 {i+1}:\n{doc['content'][:2000]}" for i, doc in enumerate(context)])
        
        full_prompt = f"{system_prompt}\n\n参考文档:\n{context_str}\n\n问题:\n{query}"
        
        try:
            response = Generation.call(
                model=self.model_name,
                prompt=full_prompt,
                temperature=0.7
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                raise ValueError(f"API error: {response.message}")
        except Exception as e:
            raise ValueError(f"LLM API error: {str(e)}")
    
    def summarize_document(self, content):
        system_prompt = """你是一个文档摘要助手。请对提供的文档内容进行简明扼要的总结。"""
        
        full_prompt = f"{system_prompt}\n\n请总结以下文档内容:\n{content[:4000]}"
        
        try:
            response = Generation.call(
                model=self.model_name,
                prompt=full_prompt,
                temperature=0.7
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                raise ValueError(f"API error: {response.message}")
        except Exception as e:
            raise ValueError(f"LLM API error: {str(e)}")