# Cary AI Platform

Draft Example of Enterprise AI infrastructure for The Cary Company.
Production-ready RAG system enabling department-specific
knowledge retrieval across organization.

Uses loaded data from: https://github.com/dylanhans/cary_test_aiplatform/blob/main/docs/detailed_hr.txt
Can load pdf, txt files for demo. Production would use real company infrastructure for retrieval.

## Architecture

- **API Layer:** FastAPI with structured logging
- **AI Orchestration:** LangChain + Azure OpenAI (GPT-4o)
- **Vector Storage:** pgvector on PostgreSQL (Can swap with pinecone, chromadb. Used due to no dependency on other applications)
- **Access Control:** Department-based document filtering
- **Audit Trail:** Full conversation logging (across departments, roles, responses)
- **Deployment:** Docker + Docker Compose

## Clone Start (Repository)

1. `cp .env.example .env` — configure API keys
2. `docker-compose up -d` — start services
3. `python scripts/ingest_documents.py` — load documents
4. Open `frontend/index.html` — start querying

## Production Roadmap

- Azure AD authentication via Microsoft Graph API
- SharePoint document sync for automatic updates
- NetSuite integration for operational data queries
- Monitoring via Azure Application Insights
- Multi-tenant isolation per department

Implementation Roadmap & Architecture
Phase 1: Foundation (Current)
✓ Authentication system (OAuth2 ready)
✓ RAG pipeline with PostgreSQL + pgvector
✓ Audit logs in middleware and error handling
✓ HR Knowledge Agent with document ingestion
✓ Multi-department support

Phase 2: Integration (Next)
▶ NetSuite ERP connector (purchase orders, inventory)
▶ Salesforce CRM integration (customer data, pipeline)
▶ Azure OpenAI deployment (production models)
▶ Real-time data sync via APIs

Phase 3: Scale & Intelligence
▶ Multi-agent orchestration
▶ Agentic workflows (approvals, follow-ups)
▶ Fine-tuned domain models
▶ Compliance & audit logging

Tech Stack
Backend: FastAPI + Python
AI: OpenAI GPT + pgvector
Database: PostgreSQL (RAG storage)
Neon (managed PostgreSQL with pgvector)
Frontend: Vanilla JS + HTML5
Railway

Next Steps:

- **Backend**: Azure App Service
- **Auth**: Azure Active Directory SSO (replacing simulated auth)
- **Document sync**: SharePoint webhook to ingest pipeline

ARCHITECTURE:

Current,

┌─────────────────────────────────────────────────────────────┐
│ USER BROWSER │
│ Vercel (Static Frontend) │
│ login.html → dashboard.html │
└─────────────────────────┬───────────────────────────────────┘
│ HTTPS REST
▼
┌─────────────────────────────────────────────────────────────┐
│ RAILWAY (FastAPI Backend) │
│ │
│ POST /api/v1/auth/login POST /api/v1/query │
│ GET /health GET /api/v1/departments │
│ │
│ ┌─────────────────┐ ┌──────────────────────────────┐ │
│ │ auth.py │ │ retrieval.py │ │
│ │ JWT tokens │ │ embed → search → generate │ │
│ └─────────────────┘ └──────────────┬───────────────┘ │
└────────────────────────────────────────┼────────────────────┘
│
┌──────────────────────────┼──────────────────┐
│ │ │
▼ ▼ │
┌─────────────────────┐ ┌─────────────────────────┐ │
│ NEON (PostgreSQL) │ │ OPENAI API │ │
│ │ │ │ │
│ documents table │ │ text-embedding-3-small │ │
│ vector(1536) │ │ gpt-4o-mini │ │
│ pgvector search │ │ │ │
│ │ └─────────────────────────┘ │
│ conversations │ │
│ table (audit log) │ │
└─────────────────────┘ │

Production,

─────────────────────────────────────────────────────────────────┐
│ CARY EMPLOYEES │
│ Microsoft 365 / Azure AD SSO │
└──────────────────────────┬──────────────────────────────────────┘
│ SSO Login
▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (React + TypeScript) │
│ Hosted on Azure Web Applications │
│ │
│ HR Agent │ Sales Agent │ Ops Agent │ Finance Agent │ CS Agent │
└──────────────────────────┬──────────────────────────────────────┘
│ HTTPS + Bearer Token
▼
┌─────────────────────────────────────────────────────────────────┐
│ API LAYER (FastAPI on Azure App Service) │
│ │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│ │ Auth Router│ │Query Router│ │Upload Router│ │
│ │ Azure AD │ │ RAG Pipeline│ │ Ingestion │ │
│ └────────────┘ └────────────┘ └────────────┘ │
└──────┬─────────────────┬──────────────────┬─────────────────────┘
│ │ │
▼ ▼ ▼
┌────────────┐ ┌─────────────────┐ ┌──────────────────────┐
│ AZURE AD │ │ AZURE POSTGRESQL│ │ AZURE OPENAI │
│ │ │ + pgvector │ │ │
│ User roles │ │ │ │ gpt-4o (deployment) │
│ Dept scope │ │ documents │ │ text-embedding-3- │
│ SSO tokens │ │ conversations │ │ small (deployment) │
└────────────┘ │ users │ └──────────────────────┘
└─────────────────┘
▲
┌──────────────┴───────────────┐
│ │
┌────────────────┐ ┌─────────────────────┐
│ SHAREPOINT │ │ NETSUITE ERP │
│ │ │ │
│ Document sync │ │ Inventory queries │
│ Webhook → │ │ Order status │
│ re-ingestion │ │ Customer records │
│ pipeline │ │ │
└────────────────┘ └─────────────────────┘
