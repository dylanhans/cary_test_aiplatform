# app/services/retrieval.py
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.llm import get_embeddings
from app.models.database import get_db
from langchain.prompts import ChatPromptTemplate
from app.services.llm import get_llm
import json
import logging

logger = logging.getLogger(__name__)

def ingest_document(
    file_path: str,
    department: str,
    doc_type: str = "policy",
    source: str = ""
):
    logger.info(f"Ingesting {file_path} for {department}")
    
    loader = TextLoader(file_path)
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=75,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_documents(documents)
    
    embeddings_service = get_embeddings()
    
    with get_db() as conn:
        cur = conn.cursor()
        ingested = 0
        
        for chunk in chunks:
            try:
                embedding = embeddings_service.embed_query(
                    chunk.page_content
                )
                cur.execute(
                    """
                    INSERT INTO documents 
                    (content, embedding, source, department, 
                     doc_type, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        chunk.page_content,
                        embedding,
                        source or file_path,
                        department,
                        doc_type,
                        json.dumps(chunk.metadata)
                    )
                )
                ingested += 1
            except Exception as e:
                logger.error(f"Failed to ingest chunk: {e}")
                continue
    
    logger.info(
        f"Ingested {ingested}/{len(chunks)} chunks "
        f"for {department}"
    )
    return ingested


SYSTEM_PROMPT = """You are an internal AI assistant for 
The Cary Company. Answer questions accurately using only 
the provided context. 

Rules:
- Only use information from the provided context
- If the answer isn't in the context, say so clearly
- Never make up information
- For HR policies, always recommend confirming with HR
  for official guidance
- Be concise and professional.
- Structure it clearly, separating each sentence or point with a new line.

Department context: {department}
"""

USER_PROMPT = """Context from internal documents:
{context}

Question: {question}

Answer:"""

def query(
    question: str,
    department: str = "General",
    session_id: str = None
) -> dict:
    
    embeddings_service = get_embeddings()
    question_embedding = embeddings_service.embed_query(question)
    
    with get_db() as conn:
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT content, source, department,
                   1 - (embedding <=> %s::vector) as similarity
            FROM documents
            WHERE department = %s 
               OR department = 'General'
            ORDER BY embedding <=> %s::vector
            LIMIT 3
            """,
            (question_embedding, department, question_embedding)
        )
        
        results = cur.fetchall()
        
        if not results:
            return {
                "answer": "No relevant information found "
                         "for this department.",
                "sources": [],
                "department": department
            }
        
        context_parts = []
        sources = []
        
        for content, source, dept, similarity in results:
            if similarity > 0.45:
                context_parts.append(content)
                if source not in sources:
                    sources.append(source)
        
        if not context_parts:
            return {
                "answer": "I couldn't find sufficiently "
                         "relevant information. Please "
                         "contact your department directly.",
                "sources": [],
                "department": department
            }
        
        context = "\n\n---\n\n".join(context_parts)
        
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT)
        ])
        
        chain = prompt | llm
        response = chain.invoke({
            "department": department,
            "context": context,
            "question": question
        })
        
        answer = response.content
        
        if session_id:
            cur.execute(
                """
                INSERT INTO conversations 
                (session_id, department, user_message,
                 assistant_response, sources)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    department,
                    question,
                    answer,
                    json.dumps(sources)
                )
            )
        
        return {
            "answer": answer,
            "sources": sources,
            "department": department
        }