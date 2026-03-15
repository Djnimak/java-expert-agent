# Java Expert AI Agent

## Overview

Java Expert AI Agent is an agentic AI assistant built as part of the **Ciklum AI Academy Engineering Track**.

The system is designed to help a Java Tech Lead or Java developer with practical engineering tasks such as:

- answering Java, Spring, and design-pattern questions
- retrieving information from an internal knowledge base using RAG
- falling back to general model knowledge when the internal KB is insufficient
- falling back to web search when both the KB and model knowledge are not enough
- generating plain Java code
- reviewing Java code with professional PR-style comments
- reflecting on its own outputs and revising them when needed

The goal of the project was to build a technically robust but still practical AI-agentic system covering the major real-world components of modern agent development:
- data preparation and contextualization
- RAG pipeline design
- tool calling
- reasoning and self-reflection
- evaluation

---

## Problem Statement

As a Java Tech Lead, one of my responsibilities is to answer technical questions, support engineering decisions, generate code examples, and professionally review the code of other developers.

Generic AI assistants can help, but they do not always:
- prioritize trusted internal documentation
- clearly separate grounded answers from fallback answers
- provide structured professional code review comments
- reflect on their own output quality

This project solves that problem by building a **Java Expert AI Agent** that:
1. uses an internal Java/Spring/design-pattern knowledge base first,
2. falls back to general model knowledge if needed,
3. falls back to web search when freshness or broader knowledge is required,
4. supports Java code generation,
5. supports structured Java code review,
6. reflects on its own output and revises when necessary.

---

## Main Capabilities

### 1. Knowledge-base-backed technical Q&A
The agent answers Java / Spring / design-pattern questions using a local internal knowledge base stored in Qdrant.

### 2. Fallback reasoning
If the internal knowledge base is weak:
- the agent first tries **general model knowledge**
- then uses **web search** if required

The final answer always indicates the source:
- `Source: Internal knowledge base`
- `Source: General model knowledge`
- `Source: Web search`

### 3. Plain Java code generation
The agent can generate plain Java code using general Java best practices.

### 4. Java code review
The agent can review user-provided Java code and return structured, professional, PR-style comments.

### 5. Self-reflection and self-correction
After generating an answer, code, or review, the agent performs a reflection step and decides whether the output should be:
- kept as-is
- or revised automatically

---

## Technology Stack

- **Python**
- **OpenAI API**
- **Sentence Transformers**
- **Qdrant**
- **PyMuPDF**
- **python-docx**

### Main libraries
- `openai`
- `sentence-transformers`
- `qdrant-client`
- `pymupdf`
- `python-docx`
- `python-dotenv`

---

## Knowledge Base

The internal knowledge base contains:
- Java and Spring Q&A materials
- design pattern documents
- a code review checklist
- source documents in:
  - `.pdf`
  - `.docx`

The system supports:
- PDF text extraction
- DOCX text extraction
- table-aware extraction for both formats

---

## Agent Workflow

Each of the below mentioned flows was manually evaluated. You can check evaluation question and evaluation scores in eval/evaluation_cases.json and eval/evaluation_results.md respectively.

### Request types
The agent classifies a user request into one of three types:
- `question_answering`
- `code_generation`
- `code_review`

### Q&A flow
1. Retrieve relevant chunks from Qdrant
2. If retrieval is strong enough, answer from the internal KB
3. If retrieval is weak, answer from general model knowledge
4. If still insufficient, use web search
5. Reflect on the final answer
6. Revise automatically if needed

### Code generation flow
1. Detect code generation request
2. Generate plain Java code
3. Reflect on the generated output
4. Revise if needed

### Code review flow
1. Detect code review request
2. Review pasted Java code
3. Return structured professional findings
4. Reflect on review quality
5. Revise if needed

---

## Project Structure

```text
java-expert-agent/
├─ data/
│  ├─ pdfs/
│  └─ docx/
├─ eval/
│  ├─ evaluation_cases.json
│  └─ evaluation_results.md
├─ src/
│  ├─ agent/
│  │  ├─ orchestrator.py
│  │  ├─ reflection.py
│  │  ├─ reflection_engine.py
│  │  └─ tools.py
│  ├─ loaders/
│  │  ├─ docx_loader.py
│  │  └─ pdf_loader.py
│  ├─ rag/
│  │  ├─ chunking.py
│  │  ├─ ingest.py
│  │  ├─ qdrant_ingest.py
│  │  └─ retrieve.py
│  ├─ config.py
│  └─ main.py
├─ architecture.mmd
├─ README.md
├─ requirements.txt
└─ .env
```

## How to Run

### Prerequisites
Before running the project, make sure you have:

- Python 3.10+ installed
- Qdrant running locally on `http://localhost:6333`
- an OpenAI API key

---

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd java-expert-agent
```

### 2. Create and activate a virtual environment

Windows PowerShell
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Create the environment file

Create a .env file in the project root: OPENAI_API_KEY=your_api_key_here

### 5. Prepare the knowledge base files (if more needed)

Place your source documents into these folders:

- data/pdfs — for Java / Spring / design-pattern PDF files
- data/docx — for DOCX files such as the code review checklist

### 6. Start Qdrant
Make sure Qdrant is running on port 6333.

### 7. Ingest the knowledge base into Qdrant

```bash
python -m src.rag.qdrant_ingest
```
This step will:
- load PDF and DOCX files
- extract text and tables
- chunk the content
- generate embeddings
- store chunks in Qdrant

### 8. Start the agent

```bash
python -m src.main
```

Example Requests

1. Question answering
   - What is the difference between @Autowired and @Inject?

2. Code generation
   - Generate a plain Java immutable Employee class with id, name, and email.

3. Code review
   - Review this Java code:

    public class A {
        public String name;
        public int age;
    }

4. Expected Behavior

The agent classifies the request and routes it to the correct flow:
- Question answering
    - internal knowledge base first
    - then general model knowledge
    - then web search if needed

- Code generation
    - generates plain Java code
    - reflects on the result
    - revises if needed

- Code review
    - reviews pasted Java code
    - returns structured findings
    - reflects on the review
    - revises if needed