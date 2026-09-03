# 🚀 Practical AI Agent Engineering: GCC Customer Support System 🇸🇦 🇦🇪 🇰🇼

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2%2B-orange.svg?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-1.3%2B-green.svg?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langchain)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorStore-purple.svg)](https://www.trychroma.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Checkpointer-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Ragas](https://img.shields.io/badge/Ragas-Evaluation-red.svg)](https://docs.ragas.io/)

A comprehensive, production-ready curriculum and practical implementation of an enterprise-grade **Customer Support Multi-Agent AI System** tailored for the Gulf / GCC region (Saudi Arabia, UAE, Kuwait, Qatar, Bahrain, Oman).

---

## 📑 Table of Contents

1. [🌟 Course Overview & Progression](#-course-overview--progression)
2. [🏗️ End-to-End System Architecture](#️-end-to-end-system-architecture)
3. [🧠 Day 1: State-First Architecture](#-day-1-state-first-architecture)
4. [🤖 Day 2: Multi-Agent Orchestration & Tool Calling](#-day-2-multi-agent-orchestration--tool-calling)
5. [🔍 Day 3: RAG, Evaluation & Reliability](#-day-3-rag-evaluation--reliability)
6. [📊 3-Day Technical Matrix & Comparison](#-3-day-technical-matrix--comparison)
7. [📁 Repository Structure](#-repository-structure)
8. [⚙️ Environment Setup & Installation](#️-environment-setup--installation)
9. [🔐 Environment Variables Configuration](#-environment-variables-configuration)
10. [🎯 Assignments & Key Takeaways](#-assignments--key-takeaways)

---

## 🌟 Course Overview & Progression

This course builds a complete, stateful, multi-agent AI customer support platform from the ground up across three progressive milestones:

```mermaid
graph LR
    subgraph Day1["🧠 Day 1: State-First Foundation"]
        D1A[Typed State Schema] --> D1B[Context Retention]
        D1B --> D1C[PostgreSQL Checkpointer]
    end
    
    subgraph Day2["🤖 Day 2: Multi-Agent & Tools"]
        D2A[Router Agent] --> D2B[Shipping Agent + Tools]
        D2B --> D2C[Error Resilience]
    end
    
    subgraph Day3["🔍 Day 3: RAG & Evaluation"]
        D3A[Policies & FAQs Chunking] --> D3B[ChromaDB Retrieval]
        D3B --> D3C[Ragas & Dialect Eval]
    end
    
    Day1 --> Day2 --> Day3
```

---

## 🏗️ End-to-End System Architecture

```mermaid
flowchart TD
    User([👤 Customer Message]) --> Router[🧭 Router Agent]
    
    Router -->|Order / Shipping Inquiry| ShippingAgent[📦 Shipping Execution Agent]
    Router -->|Policy / General FAQ| RAGNode[🔍 RAG Knowledge Node]
    Router -->|Billing / Invoice| BillingAgent[💳 Invoice Agent]
    
    subgraph ToolLayer["🛠️ Typed Tool Execution Layer"]
        ShippingAgent -->|Tool Call| LookupOrder[📦 lookup_order]
        BillingAgent -->|Tool Call| LookupInvoice[💳 lookup_invoice]
        LookupOrder --> DB[(🗄️ Orders DB)]
        LookupInvoice --> DB
    end
    
    subgraph RAGLayer["📚 RAG Knowledge Retrieval Layer"]
        RAGNode --> VectorStore[(🔮 ChromaDB Vector Store)]
        VectorStore -.-> PolicyDocs[📄 Company Policies]
        VectorStore -.-> FAQDocs[❓ 15 GCC FAQs]
    end
    
    LookupOrder --> ToolNode[🔄 Tool Execution Node]
    LookupInvoice --> ToolNode
    ToolNode --> ShippingAgent
    
    ShippingAgent --> Responder[💬 Response Generator]
    RAGNode --> Responder
    BillingAgent --> Responder
    
    Responder --> Checkpoint[(🐘 PostgreSQL Async Checkpointer)]
    Checkpoint --> Client([📱 Verified Context-Aware Reply])
```

---

## 🧠 Day 1: State-First Architecture

**Notebook**: [`notebook/day1_state_first_architecture_practical.ipynb`](file:///d:/course/practs%20for%20course/notebook/day1_state_first_architecture_practical.ipynb)

### 🎯 Core Principles
- **State as Single Source of Truth**: The LLM is just a processor; the `State` holds business reality.
- **Golden Rule of State**: 📌 **Topic Change $\neq$ State Reset**. When a customer shifts from delayed shipping to billing, their customer ID, tier, and session history must stay intact.
- **Durable Sessions**: In-memory state dies on restart; persistent checkpointers make conversations resilient.

### 🧩 Unified State Schema
```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class CustomerContext(TypedDict):
    customer_id: str
    name: str
    tier: str         # VIP, Regular, Premium
    country: str      # KSA, UAE, Kuwait

class ComplaintContext(TypedDict):
    ticket_id: str
    category: str     # shipping, billing, technical
    resolution_status: str  # open, in_progress, resolved

class SupportState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    customer: CustomerContext
    complaint: ComplaintContext
```

### 🐘 PostgreSQL Checkpointer
```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# Durable state persistence across restarts
async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
    await checkpointer.setup()
    app = workflow.compile(checkpointer=checkpointer)
```

---

## 🤖 Day 2: Multi-Agent Orchestration & Tool Calling

**Notebook**: [`notebook/Day2_Multi_Agent_Tool_Calling.ipynb`](file:///d:/course/practs%20for%20course/notebook/Day2_Multi_Agent_Tool_Calling.ipynb)

### 🎯 Core Principles
- **Agent Specialization**: Router classifies intent without side-effects; execution agents have narrow scoped tools.
- **Pydantic Typed Tools**: Strict argument validation, clear docstrings, and robust error returns.
- **Execution Loop**: Handling `tool_calls` round-trips through LangGraph conditional edges.
- **Resilient Error Paths**: If an order is missing (`Order 9999`), return a polite recovery message rather than crashing.

### 🛠️ Typed Tool Example
```python
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class OrderLookupInput(BaseModel):
    order_id: str = Field(description="5-digit numeric order ID, e.g. '5501'")

@tool("lookup_order", args_schema=OrderLookupInput)
def lookup_order(order_id: str) -> dict:
    """Retrieve real-time shipping and delivery status for a customer order."""
    if order_id in DATABASE:
        return {"status": "success", "data": DATABASE[order_id]}
    return {"status": "error", "message": f"Order #{order_id} not found."}
```

### 🔄 Multi-Turn Tool Execution Trace
```text
Customer: "أين شحنتي رقم 5501؟"
   ↓
Router Agent ──► routes to 'shipping_agent'
   ↓
Shipping Agent ──► emits tool_call: lookup_order(order_id='5501')
   ↓
Tool Node ──► executes lookup_order ──► returns {status: 'Out for Delivery', courier: 'SMSA'}
   ↓
Shipping Agent ──► parses tool result ──► generates friendly Arabic response
```

---

## 🔍 Day 3: RAG, Evaluation & Reliability

**Notebook**: [`notebook/Day3_RAG_Evaluation_Reliability.ipynb`](file:///d:/course/practs%20for%20course/notebook/Day3_RAG_Evaluation_Reliability.ipynb)

### 🎯 Core Principles
- **Grounded Generation**: The LLM answers **only** from retrieved documents to completely eliminate hallucination.
- **Structured Knowledge Base**:
  - 📄 [`data/company_policies.md`](file:///d:/course/practs%20for%20course/data/company_policies.md): Comprehensive policies on shipping, returns, refunds, Tamara/Tabby BNPL.
  - ❓ [`data/faqs.json`](file:///d:/course/practs%20for%20course/data/faqs.json): 15 curated GCC Q&As with metadata tagging.
- **Two-Stage Evaluation**:
  - **Stage 1 (Retrieval)**: Did we retrieve the right chunk? (Source Accuracy & Keyword Hit Rate).
  - **Stage 2 (Generation)**: Did the LLM answer faithfully without fabricating policies? (Ragas Faithfulness $\ge 0.85$).

### ✂️ Chunking & Metadata Pipeline
```python
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 1. Split on Markdown headers (#, ##, ###)
header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")])
policy_docs = header_splitter.split_text(policy_text)

# 2. Recursive character splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=300)
policy_chunks = text_splitter.split_documents(policy_docs)

# 3. Vector store indexing
vectorstore = Chroma.from_documents(all_docs, OpenAIEmbeddings(model="text-embedding-3-small"))
```

### 🇸🇦 Handling Gulf Dialects & Informal Queries
Tested against 20 benchmark queries in [`data/test_eval_queries.json`](file:///d:/course/practs%20for%20course/data/test_eval_queries.json):
- 🇸🇦 *«كم ياخذ التوصيل للرياض؟»* (Delivery duration)
- 🇦🇪 *«كيف أرجع الشغلة اللي اشتريتها؟»* (Return process)
- 🇰🇼 *«ابا ارجع القطعه شسوي بالظبط»* (Step-by-step return)
- 💳 *«اذا رجعت الغرض اللي دفعته بتقسيط تمارا بيوقفون الاقساط الباقية؟»* (Tamara BNPL cancellation)
- 🛡️ *«هل يمكنني الحصول على خصم 50%؟»* (Anti-hallucination test $\rightarrow$ gracefully declined)

---

## 📊 3-Day Technical Matrix & Comparison

| Feature / Component | 🧠 Day 1 (State Architecture) | 🤖 Day 2 (Multi-Agent & Tools) | 🔍 Day 3 (RAG & Reliability) |
| :--- | :--- | :--- | :--- |
| **Primary Focus** | State modeling & persistence | Agent routing & tool calling | Knowledge retrieval & evaluation |
| **Core Framework** | `LangGraph`, `TypedDict` | `LangGraph`, `Pydantic` tools | `LangChain`, `ChromaDB`, `Ragas` |
| **LLM Dependency** | Pure state machine (No LLM) | Bound LLM (`bind_tools`) | Grounded LLM (`gpt-4o-mini`) |
| **Data Storage** | PostgreSQL Checkpoints | In-Memory Database + Postgres | Chroma Vector Store + Embeddings |
| **Persistence Unit** | `thread_id` session states | Multi-turn tool execution trace | Vector embeddings + Golden datasets |
| **Evaluation Method** | State retention assertion | Error path & schema validation | Source accuracy & Ragas Faithfulness |
| **Key Failure Mode** | Topic switch data loss | Tool schema mismatch / unhandled errors | Hallucinations & poor retrieval |

---

## 📁 Repository Structure

```text
practs-for-course/
│
├── 📁 data/                                  # 📚 Course Knowledge Base & Eval Sets
│   ├── 📄 company_policies.md                 # GCC e-commerce shipping, returns & BNPL policy
│   ├── ❓ faqs.json                           # 15 structured FAQ records with rich metadata
│   └── 🧪 test_eval_queries.json              # 20 benchmark test queries (Standard & Gulf)
│
├── 📁 notebook/                              # 📓 Interactive Hands-on Notebooks
│   ├── 🚀 day1_state_first_architecture_practical.ipynb   # Day 1: State & Checkpoints
│   ├── 🤖 Day2_Multi_Agent_Tool_Calling.ipynb              # Day 2: Multi-Agent & Tools
│   └── 🔍 Day3_RAG_Evaluation_Reliability.ipynb           # Day 3: RAG, Chroma & Eval
│
├── 📄 .env                                   # 🔐 API keys and DB connection strings
├── 📄 pyproject.toml                         # 📦 Project metadata & dependencies
├── 📄 requirements.txt                       # 📋 Pinned Python requirements
└── 📄 README.md                              # 📖 Comprehensive Master Documentation
```

---

## ⚙️ Environment Setup & Installation

### 1. Clone & Navigate
```bash
git clone <repository-url>
cd "practs for course"
```

### 2. Create Virtual Environment with `uv` or `venv`
Using **`uv`** (Recommended):
```bash
uv venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux / macOS
uv pip install -r requirements.txt
```

Or using standard **`pip`**:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔐 Environment Variables Configuration

Create or update your `.env` file in the root directory:

```ini
# ==========================================
# 🤖 LLM API Keys (Choose at least one)
# ==========================================
OPENAI_API_KEY="sk-..."
GROQ_API_KEY="gsk_..."
GEMINI_API_KEY="AIza..."

# ==========================================
# 🐘 PostgreSQL Checkpointer Database
# ==========================================
POSTGRES_DB_URI="postgresql://postgres:your_password@localhost:5432/langgraph_db"
```

---

## 🎯 Assignments & Key Takeaways

### 🏆 Day 1 Assignment
- [x] Implement `CustomerContext` and `ComplaintContext` TypedDicts.
- [x] Verify context retention when customer switches topics mid-conversation.
- [x] Export the Mermaid graph diagram.
- [x] Connect `AsyncPostgresSaver` and test persistent multi-session recovery.

### 🏆 Day 2 Assignment
- [x] Build typed Pydantic tool `lookup_order`.
- [x] Build participant exercise tool `lookup_invoice` with invoice number validation.
- [x] Implement the Router Agent and Shipping Execution Agent.
- [x] Test missing order resilience (`Order #9999`).

### 🏆 Day 3 Assignment
- [x] Ingest & split `company_policies.md` and `faqs.json`.
- [x] Create ChromaDB vector store with OpenAI embeddings.
- [x] Evaluate retrieval accuracy across 20 Standard and Gulf dialect queries.
- [x] Test anti-hallucination behavior on unsupported discount questions.
- [x] Experiment with retriever hyperparameter $k \in \{2, 4, 6\}$.

---

### 🎓 Summary of Golden Rules
1. 🧠 **State First**: State is the single source of truth; never rely solely on chat history.
2. 🔄 **Topic Switch $\neq$ State Reset**: Always preserve customer context across topic changes.
3. 🛠️ **Narrow Typed Tools**: Give agents specific, validated tools with deterministic return schemas.
4. 🔍 **Evaluate Retrieval First**: Separate document retrieval accuracy from answer generation quality.
5. 🛡️ **Zero Hallucination**: Constrain LLM responses strictly to retrieved, verified context.

*Happy Building! 🚀*
