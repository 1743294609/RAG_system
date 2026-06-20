import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from dashscope import TextEmbedding

load_dotenv()

class VectorStore:
    def __init__(self):
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v1")
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.top_k = int(os.getenv("TOP_K", 5))
    
    def _get_connection(self):
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "123456"),
            dbname=os.getenv("POSTGRES_DB", "postgres")
        )
    
    def create_embedding(self, text):
        try:
            response = TextEmbedding.call(
                model=self.embedding_model,
                input=text,
                api_key=self.api_key
            )
            
            if response.status_code == 200:
                return response.output['embeddings'][0]['embedding']
            else:
                raise ValueError(f"Embedding API error: {response.message}")
        except Exception as e:
            raise ValueError(f"Failed to create embedding: {str(e)}")
    
    def add_document(self, filename, file_type, content):
        embedding = self.create_embedding(content)
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            cur.execute(
                "INSERT INTO documents (filename, file_type, content, embedding) VALUES (%s, %s, %s, %s)",
                (filename, file_type, content, embedding_str)
            )
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            raise ValueError(f"Failed to add document: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def search_similar(self, query, top_k=None):
        k = top_k or self.top_k
        query_embedding = self.create_embedding(query)
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            cur.execute(f"""
                SELECT id, filename, file_type, content, 
                       1 - (embedding <=> '{embedding_str}'::vector) AS similarity
                FROM documents
                ORDER BY embedding <=> '{embedding_str}'::vector
                LIMIT {k};
            """)
            
            results = cur.fetchall()
            cur.close()
            return results
        except Exception as e:
            raise ValueError(f"Failed to search documents: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def get_all_documents(self):
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT id, filename, file_type, created_at FROM documents ORDER BY created_at DESC;")
            results = cur.fetchall()
            cur.close()
            return results
        except Exception as e:
            raise ValueError(f"Failed to get documents: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def delete_document(self, doc_id):
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
            conn.commit()
            cur.close()
            return cur.rowcount > 0
        except Exception as e:
            if conn:
                conn.rollback()
            raise ValueError(f"Failed to delete document: {str(e)}")
        finally:
            if conn:
                conn.close()