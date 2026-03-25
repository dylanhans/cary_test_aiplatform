import os
import json
import psycopg2
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def ingest(file_path: str, department: str = "HR"):
    print(f"Loading {file_path}...")
    loader = TextLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=75,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    ingested = 0
    for chunk in chunks:
        embedding = embeddings.embed_query(chunk.page_content)
        cur.execute(
            """
            INSERT INTO documents
            (content, embedding, source, department, doc_type, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                chunk.page_content,
                embedding,
                file_path,
                department,
                "policy",
                json.dumps(chunk.metadata)
            )
        )
        ingested += 1
        print(f"  Chunk {ingested}/{len(chunks)}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"Done. {ingested} chunks ingested for {department}.")

if __name__ == "__main__":
    ingest("docs/Nicoles_hr_policy_samples.txt", "HR")