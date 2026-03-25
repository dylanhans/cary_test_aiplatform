# app/services/llm.py
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
from app.core.config import settings

def get_llm():
    if settings.use_azure:
        return AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            azure_deployment=settings.azure_openai_deployment,
            api_version="2024-02-01",
            temperature=0.1
        )
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model="gpt-4o",
        temperature=0.1
    )

def get_embeddings():
    if settings.use_azure:
        return AzureOpenAIEmbeddings(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            azure_deployment=settings.azure_openai_embedding_deployment,
            api_version="2024-02-01"
        )
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model="text-embedding-3-small"
    )