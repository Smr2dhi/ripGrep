# 📚 GrepRAG — AI Knowledge Assistant

GrepRAG is a lightweight **Retrieval-Augmented Generation (RAG)** system that answers questions from your own documents.

Instead of a vector database, it uses [**ripgrep**](https://github.com/BurntSushi/ripgrep) (`rg`) for fast, exact keyword search over the knowledge base. An LLM generates relevant search keywords, `ripgrep` finds matching files and lines, and the retrieved context is expanded before being passed to a **Gemini LLM** through the OpenAI Agents SDK.

The final response is grounded in the retrieved document context and includes file and line citations.

* **Backend:** FastAPI + OpenAI Agents SDK + Gemini + ripgrep
* **Frontend:** Streamlit chat UI
* **Storage:** Flat files on disk (`documents/`, `memory/`, `logs/`)
* **Deployment:** Docker + Docker Compose

---

## Table of Contents

1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [How it works](#how-it-works)
4. [Project structure](#project-structure)
5. [File-by-file explanation](#file-by-file-explanation)
6. [Setup & installation](#setup--installation)
7. [Environment variables](#environment-variables)
8. [Running the app](#running-the-app)
9. [Docker deployment](#docker-deployment)
10. [Docker environment handling](#docker-environment-handling)
11. [API reference](#api-reference)
12. [Testing](#testing)
13. [Useful Docker commands](#useful-docker-commands)
14. [Security](#security)
15. [Known limitations / notes](#known-limitations--notes)
16. [Future improvements](#future-improvements)
17. [Project summary](#project-summary)

---

## Features

* 📄 Upload documents
* 📚 Support for:

  * `.txt`
  * `.md`
  * `.pdf`
  * `.docx`
* 🔎 Keyword-based document retrieval using **ripgrep**
* 🤖 Gemini LLM integration
* 🛠️ OpenAI Agents SDK tool calling
* 🧠 Conversational memory
* 📌 File and line-based citations
* 🚫 Grounded answers to reduce hallucination
* 📋 List available knowledge-base files
* 📝 Application logging
* ⚡ Fast exact keyword search
* 🌐 FastAPI backend
* 🎨 Streamlit frontend
* 🐳 Separate Docker containers for frontend and backend
* 💾 Persistent documents, memory, and logs
* 🔐 Environment-variable based API key management

---

## Technology Stack

| Technology                       | Purpose                              |
| -------------------------------- | ------------------------------------ |
| **Python**                       | Main programming language            |
| **FastAPI**                      | Backend REST API                     |
| **OpenAI Agents SDK**            | Agent orchestration and tool calling |
| **Google Gemini**                | Large Language Model                 |
| **Gemini OpenAI-compatible API** | Connects Gemini with the Agents SDK  |
| **ripgrep (`rg`)**               | Exact keyword-based retrieval        |
| **Streamlit**                    | Frontend chat interface              |
| **Pydantic**                     | Request and response validation      |
| **python-docx**                  | DOCX text extraction                 |
| **pypdf**                        | PDF text extraction                  |
| **JSON**                         | Conversation memory storage          |
| **python-dotenv**                | Environment configuration            |
| **Docker**                       | Containerization                     |
| **Docker Compose**               | Multi-container orchestration        |
| **Uvicorn**                      | FastAPI application server           |

---

## How it works

1. A user **uploads a document** (`.txt`, `.md`, `.pdf`, or `.docx`) through the Streamlit UI.

2. The backend saves the uploaded file into:

   ```text
   documents/
   ```

3. The ingestion loader extracts the document text for validation and processing.

4. The user **asks a question** in the chat.

5. The Gemini agent receives the question together with the available conversation memory.

6. The agent decides whether a tool is required.

   Available tools:

   * `list_files` → lists documents available in the knowledge base.
   * `grep_search` → searches the knowledge base using keywords.

7. For a knowledge-base question, the LLM generates simple search keywords.

   For example:

   ```python
   [
       "authentication",
       "auth",
       "login",
       "verify_token"
   ]
   ```

8. `grep_search()` runs `ripgrep` with those keywords.

   Example:

   ```bash
   rg -n -i -F -e authentication -e auth -e login -e verify_token documents
   ```

9. `ripgrep` returns matching files, line numbers, and matching text.

10. The context retrieval layer expands the matching lines using surrounding lines so that the LLM receives meaningful context instead of only one matching line.

11. Duplicate matches are removed and the resulting context is limited to a configured maximum size.

12. The agent uses the retrieved context to generate a grounded answer.

13. The response follows the required:

```text
ANSWER:

...

SOURCES:

- filename:line
```

format.

14. If relevant information cannot be found, the assistant returns:

```text
I do not know based on the current knowledge base.
```

15. The question and answer are saved into `ConversationMemory`.

16. Conversation memory is persisted to:

```text
memory/conversation.json
```

17. The Streamlit frontend displays the answer and sources.

This approach treats **grep as the retriever** instead of using embeddings and a vector database.

It is simple, fast, and explainable because each retrieved result can be traced back to a real file and line.

---

## Project structure

```text
ripGrep/
├── README.md                         # Project documentation
├── .env                              # Environment variables / secrets
├── .gitignore                        # Git exclusions
├── .dockerignore                     # Docker build-context exclusions
├── docker-compose.yml                # Frontend + backend orchestration
│
├── backend/
│   ├── Dockerfile                    # Backend Docker image
│   ├── req.txt                       # Backend dependencies
│   ├── __init__.py
│   ├── main.py                       # FastAPI app and API endpoints
│   ├── config.py                     # Configuration and paths
│   ├── models.py                     # Pydantic request/response models
│   ├── prompt.py                     # Agent instructions and refusal text
│   ├── llm.py                        # Gemini + Agents SDK integration
│   ├── grep_tool.py                  # list_files and grep_search tools
│   ├── context_retrieval.py          # Context expansion and retrieval
│   ├── conversation.py               # Conversation memory
│   │
│   └── ingestion/
│       ├── loader.py                 # TXT/MD/PDF/DOCX extraction
│       └── __init__.py
│
├── frontend/
│   ├── Dockerfile                    # Frontend Docker image
│   ├── req.txt                       # Frontend dependencies
│   └── streamlit_app.py              # Streamlit chat UI
│
├── documents/                        # Uploaded knowledge-base files
│
├── memory/
│   └── conversation.json             # Persisted conversation memory
│
├── logs/
│   └── app.log                       # Application logs
│
├── tests/
│   ├── test_context_retrieval.py     # Context retrieval tests
│   └── test_loader.py                # Loader testing utility
│
└── utils/
    └── logging.py                    # Shared logger factory
```

---

# File-by-file explanation

## `backend/main.py`

The main FastAPI application entry point.

It defines the backend API endpoints.

### `POST /upload`

Responsible for:

* Receiving an uploaded file
* Validating the file extension
* Saving the file into `documents/`
* Calling `load_document()`
* Confirming that the uploaded file can be processed
* Returning document metadata

Supported extensions:

```text
.txt
.md
.pdf
.docx
```

### `POST /ask`

Responsible for:

* Receiving the user's question
* Passing the question to `LLMClient`
* Running the agent
* Returning the generated answer
* Returning source information
* Handling errors

The endpoint accepts:

```json
{
  "question": "How does token verification work?"
}
```

A shared `LLMClient` instance is created when the application starts, allowing its conversation memory to remain available during the lifetime of the backend process.

---

## `backend/config.py`

Contains centralized application configuration.

It manages values such as:

```text
GEMINI_API_KEY
GEMINI_ENDPOINT
GEMINI_MODEL
DOCUMENTS_DIR
```

The application uses environment variables instead of hard-coding secrets.

The documents directory is resolved relative to the project.

---

## `backend/models.py`

Contains Pydantic models used by the API.

Important models include:

### `AskRequest`

Validates incoming questions.

The question must:

* Not be empty
* Stay within the configured word limit

### `SourceCitation`

Represents structured source information.

It is reserved for structured citation handling.

### `AskResponse`

Defines the structure returned by `/ask`.

---

## `backend/prompt.py`

Contains the main agent instructions.

The instructions control:

* How greetings are handled
* When tools should be called
* When `list_files` should be used
* When `grep_search` should be used
* How keywords should be generated
* How conversation history should be used
* How retrieved context should be used
* How citations should be returned
* How unsupported questions should be handled

The fixed refusal answer is:

```text
I do not know based on the current knowledge base.
```

The prompt also prevents the model from treating conversation history as a replacement for knowledge-base evidence.

---

## `backend/llm.py`

Contains the main LLM orchestration layer.

The `LLMClient` class is responsible for connecting the application to Gemini through its OpenAI-compatible API.

It configures:

* `AsyncOpenAI`
* Gemini endpoint
* Gemini model
* OpenAI Agents SDK
* Agent instructions
* Agent tools
* Conversation memory

The agent uses the tools from:

```text
backend/grep_tool.py
```

The main method:

```python
llm_call(question)
```

performs the LLM request.

The general process is:

```text
Question
   ↓
Conversation memory
   ↓
Agent prompt
   ↓
Runner.run()
   ↓
Tool calls if required
   ↓
Final answer
   ↓
Save conversation
```

The class also handles model and OpenAI-compatible API errors.

---

## `backend/grep_tool.py`

Contains the agent-callable retrieval tools.

### `list_files()`

Lists files available in:

```text
documents/
```

This tool is useful when users ask what documents are available.

---

### `grep_search(keywords)`

Searches the knowledge base using `ripgrep`.

The function accepts a list:

```python
[
    "authentication",
    "login",
    "verify_token"
]
```

It builds a command similar to:

```bash
rg -n -i -F -e authentication -e login -e verify_token documents
```

### ripgrep options

#### `-n`

Includes line numbers.

#### `-i`

Performs case-insensitive search.

#### `-F`

Treats keywords as literal strings.

#### `-e`

Allows multiple search patterns.

After getting matches, the function passes them to the context retrieval layer.

---

## `backend/context_retrieval.py`

Responsible for converting raw grep matches into useful context.

The retrieval process is:

```text
grep matches
     ↓
Parse filename + line number
     ↓
Group nearby matches
     ↓
Expand surrounding lines
     ↓
Merge overlapping ranges
     ↓
Remove duplicate lines
     ↓
Apply maximum character limit
     ↓
Return context
```

For example, if line `20` matches and the configured context window is `3`, the system can retrieve surrounding lines approximately from:

```text
17 → 23
```

This gives the LLM more context around the matching keyword.

The retrieved context is also limited to a maximum number of characters to avoid creating unnecessarily large prompts.

---

## `backend/conversation.py`

Contains the `ConversationMemory` class.

Conversation history is persisted in:

```text
memory/conversation.json
```

The memory keeps recent question-answer pairs.

When older history exceeds the configured limit, older turns are moved into a textual summary.

The stored information can contain:

```text
summary
history
```

The memory is then added to the next user question so that follow-up questions can be understood.

For example:

```text
User:
How is authentication handled?

Assistant:
Authentication is handled through the login system...
```

Follow-up:

```text
User:
What method did you mention earlier?
```

The previous conversation helps the agent understand what `"earlier"` refers to.

---

## `backend/ingestion/loader.py`

Responsible for extracting text from uploaded documents.

Supported file types:

```text
.txt
.md
.docx
.pdf
```

### TXT / Markdown

These files are read directly as UTF-8 text.

### DOCX

DOCX files are processed using `python-docx`.

The loader extracts:

* Paragraphs
* Table content

Tables are flattened into readable text.

### PDF

PDF files are processed using `pypdf`.

Pages are processed individually and page markers can be added to the extracted text.

The returned structure contains information such as:

```python
{
    "text": "...",
    "document_name": "example.pdf",
    "file_type": "pdf",
    "pages": [...]
}
```

The loader raises an error for unsupported file extensions.

---

## `frontend/streamlit_app.py`

Contains the Streamlit frontend.

The frontend provides:

### Sidebar

* Backend health check
* File upload
* Uploaded document information
* Conversation controls
* Supported file information

### Main area

* Chat interface
* User messages
* Assistant responses
* Sources
* Welcome screen

When the user submits a question, Streamlit sends a request to:

```text
POST /ask
```

The frontend then renders the response.

The frontend does not directly call Gemini.

---

## `utils/logging.py`

Contains the shared logging setup.

The logger writes application logs to:

```text
logs/app.log
```

Logging helps track:

* Application startup
* API requests
* Tool calls
* Search operations
* File names
* Errors
* Debugging information

The logger also avoids attaching duplicate handlers when multiple modules request a logger.

---

## `tests/test_context_retrieval.py`

Contains tests for context retrieval.

The tests verify that grep matches are correctly expanded with surrounding lines.

---

## `tests/test_loader.py`

Contains a small testing utility for manually testing document loading through a FastAPI endpoint.

It can be used independently when debugging the document loader.

---

## `backend/req.txt`

Contains backend Python dependencies.

Typical dependencies include:

```text
fastapi
uvicorn
openai
openai-agents
pydantic
python-dotenv
python-docx
pypdf
python-multipart
```

---

## `frontend/req.txt`

Contains frontend dependencies.

The main dependency is:

```text
streamlit
```

---

## `documents/`

Runtime directory containing uploaded knowledge-base files.

Example:

```text
documents/
├── auth.txt
├── company.md
├── policies.txt
└── guide.pdf
```

---

## `memory/`

Stores conversation memory.

```text
memory/
└── conversation.json
```

---

## `logs/`

Stores application logs.

```text
logs/
└── app.log
```

---

# Setup & installation

## Prerequisites

Install the following:

* **Python 3.11+**
* **ripgrep**
* **Docker Desktop** if using Docker
* A **Google Gemini API key**

---

## 1. Clone the repository

```bash
git clone https://github.com/Smr2dhi/ripGrep.git
```

Move into the project:

```bash
cd ripGrep
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

---

## 3. Install dependencies

Install backend dependencies:

```bash
pip install -r backend/req.txt
```

Install frontend dependencies:

```bash
pip install -r frontend/req.txt
```

---

## 4. Install ripgrep

### macOS

```bash
brew install ripgrep
```

### Ubuntu / Debian

```bash
sudo apt-get install ripgrep
```

### Windows

Using Chocolatey:

```bash
choco install ripgrep
```

Or install ripgrep through another Windows package manager.

Verify installation:

```bash
rg --version
```

The application requires `rg` to be available on the system `PATH` when running outside Docker.

---

# Environment variables

Create:

```text
ripGrep/.env
```

Example:

```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=your_gemini_model
GEMINI_ENDPOINT=https://generativelanguage.googleapis.com/v1beta/openai/
```

Do not commit the `.env` file to GitHub.

---

## Environment variable reference

| Variable          | Required | Default                           | Purpose                              |
| ----------------- | -------- | --------------------------------- | ------------------------------------ |
| `GEMINI_API_KEY`  | Yes      | None                              | Authentication key for Gemini        |
| `GEMINI_MODEL`    | Yes      | None                              | Gemini model used by the application |
| `GEMINI_ENDPOINT` | No       | Gemini OpenAI-compatible endpoint | Gemini API base URL                  |

---

# Running the app

When running without Docker, the backend and frontend are started separately.

## 1. Start the backend

From the project root:

```bash
uvicorn backend.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

## 2. Start the frontend

Open another terminal.

Activate the virtual environment if necessary:

```bash
.venv\Scripts\activate
```

Then:

```bash
streamlit run frontend/streamlit_app.py
```

The Streamlit application normally runs at:

```text
http://localhost:8501
```

---

## Local application flow

```text
Browser
   ↓
Streamlit
   ↓
FastAPI
   ↓
Agents SDK
   ↓
Gemini Agent
   ↓
grep_search()
   ↓
ripgrep
   ↓
documents/
```

---

# Docker deployment

GrepRAG uses separate Docker containers for the backend and frontend.

```text
Backend container
    ↓
FastAPI + Gemini + Agents SDK + ripgrep

Frontend container
    ↓
Streamlit
```

The two services are managed using:

```text
docker-compose.yml
```

---

## Backend Dockerfile

Location:

```text
backend/Dockerfile
```

The backend image contains the backend application and its dependencies.

It also installs the required `ripgrep` executable inside the backend container.

The backend exposes:

```text
8000
```

---

## Frontend Dockerfile

Location:

```text
frontend/Dockerfile
```

The frontend image contains the Streamlit application and frontend dependencies.

The frontend exposes:

```text
8501
```

---

# Docker Compose

The current Compose configuration is:

```yaml
services:

  backend:
    container_name: greprag-backend

    build:
      context: .
      dockerfile: backend/Dockerfile

    image: greprag-backend

    ports:
      - "8000:8000"

    env_file:
      - .env

    environment:
      TZ: Asia/Kolkata

    volumes:
      - ./documents:/app/documents
      - ./memory:/app/memory
      - ./logs:/app/logs

    restart: unless-stopped


  frontend:
    container_name: greprag-frontend

    build:
      context: .
      dockerfile: frontend/Dockerfile

    image: greprag-frontend

    ports:
      - "8501:8501"

    environment:
      API_URL: http://backend:8000
      TZ: Asia/Kolkata

    depends_on:
      - backend

    restart: unless-stopped
```

---

# Docker environment handling

The root `.env` file is read by Docker Compose through:

```yaml
env_file:
  - .env
```

This passes the environment variables into the backend container at runtime.

It does **not** mean the `.env` file is copied into the Docker image.

The `.dockerignore` file can still contain:

```text
.env
```

because `.dockerignore` controls the Docker build context, while `env_file` is handled by Docker Compose separately.

---

## Verify the API key exists inside the container

To verify that the backend received the API key without printing the secret:

```bash
docker exec greprag-backend python -c "import os; print(bool(os.getenv('GEMINI_API_KEY')))"
```

Expected:

```text
True
```

Never print the actual API key into the terminal or logs.

---

# Docker volumes

The backend uses these mounted directories:

```yaml
volumes:
  - ./documents:/app/documents
  - ./memory:/app/memory
  - ./logs:/app/logs
```

### Documents

```text
./documents
```

is mounted to:

```text
/app/documents
```

### Memory

```text
./memory
```

is mounted to:

```text
/app/memory
```

### Logs

```text
./logs
```

is mounted to:

```text
/app/logs
```

This allows documents, memory, and logs to persist outside the containers.

---

# Docker networking

Inside Docker Compose, the frontend communicates with the backend using the Compose service name:

```text
http://backend:8000
```

The frontend should not use:

```text
http://localhost:8000
```

for backend communication from inside the container.

Inside the frontend container, `localhost` refers to the frontend container itself.

The correct Docker communication is:

```text
frontend container
       ↓
backend:8000
       ↓
backend container
```

---

# Build and start Docker

From the project root:

```bash
docker compose up --build -d
```

The `--build` option rebuilds the images before starting the containers.

---

# Start already-built containers

If the images have already been built:

```bash
docker compose up -d
```

There is no need to rebuild every time.

---

# Check Docker containers

```bash
docker ps
```

You should see containers similar to:

```text
greprag-backend
greprag-frontend
```

To see stopped containers as well:

```bash
docker ps -a
```

---

# Access the application

### Streamlit frontend

```text
http://localhost:8501
```

### FastAPI backend

```text
http://localhost:8000
```

### FastAPI Swagger

```text
http://localhost:8000/docs
```

---

# API reference

## `POST /upload`

Uploads a document into the knowledge base.

### Supported file types

```text
.txt
.md
.pdf
.docx
```

### Request

The endpoint expects:

```text
multipart/form-data
```

with the uploaded file in the:

```text
file
```

field.

### Example response

```json
{
  "message": "Document uploaded successfully",
  "filename": "auth.txt",
  "file_type": ".txt",
  "document": {
    "text": "...",
    "document_name": "auth.txt",
    "file_type": "txt",
    "pages": null
  }
}
```

### Possible errors

```text
400
```

for invalid upload information or unsupported file types.

```text
500
```

for document save or processing failures.

---

# `POST /ask`

Asks a question against the knowledge base.

### Request

```json
{
  "question": "How does token verification work?"
}
```

### Question validation

The question must be:

* Non-empty
* Within the configured word limit

### Example response

```json
{
  "question": "How does token verification work?",
  "answer": "ANSWER:\n...\n\nSOURCES:\n- auth.txt:4",
  "sources": [],
  "mode": "live"
}
```

The citation is currently included inside the answer text.

---

# Testing

Run the test suite:

```bash
pytest tests/
```

Or:

```bash
pytest
```

---

## `tests/test_context_retrieval.py`

Tests the context retrieval logic.

It verifies that:

```text
grep match
    ↓
matching line
    ↓
surrounding lines
```

are correctly converted into context.

---

## `tests/test_loader.py`

Provides a small FastAPI testing utility for manually testing document loading.

It can be run with:

```bash
uvicorn tests.test_loader:app --reload
```

---

# Useful Docker commands

## Build images

```bash
docker compose build
```

## Build and start

```bash
docker compose up --build -d
```

## Start

```bash
docker compose up -d
```

## Stop and remove containers

```bash
docker compose down
```

## Restart

```bash
docker compose restart
```

## Check running containers

```bash
docker ps
```

## Check all containers

```bash
docker ps -a
```

## Backend logs

```bash
docker logs -f greprag-backend
```

## Frontend logs

```bash
docker logs -f greprag-frontend
```

## Enter backend container

```bash
docker exec -it greprag-backend /bin/bash
```

If Bash is unavailable:

```bash
docker exec -it greprag-backend /bin/sh
```

## Check ripgrep inside backend

```bash
docker exec greprag-backend rg --version
```

## Check API key exists

```bash
docker exec greprag-backend python -c "import os; print(bool(os.getenv('GEMINI_API_KEY')))"
```

---

# Data persistence

The following directories contain runtime data:

```text
documents/
memory/
logs/
```

They are mounted into the backend container through Docker volumes.

Therefore:

```text
docker compose down
```

does not remove the files stored in these host directories.

For example:

```text
documents/
├── auth.txt
├── company.md
└── policy.txt
```

will remain available after the containers are recreated.

---

# Security

Important security practices:

* Never commit `.env`
* Never hard-code the Gemini API key
* Never print the actual API key
* Do not copy `.env` into Docker images
* Keep `.env` in `.gitignore`
* Keep `.env` in `.dockerignore`
* Validate uploaded file extensions
* Do not expose unnecessary backend endpoints publicly
* Protect uploaded documents if they contain sensitive information
* Add authentication before exposing the application publicly

The frontend does not need the Gemini API key.

The Gemini API key should remain on the backend.

---

# Known limitations / notes

## 1. PDF/DOCX searchability

The current ingestion loader extracts text from PDF and DOCX files.

However, `grep_search()` searches the files in `documents/` using `ripgrep`.

Plain-text files such as:

```text
.txt
.md
```

are naturally searchable by ripgrep.

PDF and DOCX files are binary formats and cannot be meaningfully searched as plain text by ripgrep.

The current loader extracts their text during upload for validation and processing, but the extracted text is not currently written as a searchable `.txt` sidecar.

A future improvement would be:

```text
uploaded PDF/DOCX
        ↓
extract text
        ↓
save searchable .txt file
        ↓
ripgrep searches extracted text
```

---

## 2. Keyword-based retrieval

GrepRAG currently uses literal keyword search.

It does not currently perform semantic similarity search.

For example, a document may contain:

```text
authorization
```

while the user's question contains:

```text
permissions
```

These concepts may be related, but literal search will not automatically understand that relationship.

The quality of retrieval therefore depends partly on the keywords generated by the LLM.

---

## 3. No vector database

The current implementation intentionally does not use:

```text
FAISS
Pinecone
Chroma
Weaviate
Milvus
```

or other vector databases.

This keeps the system simple and transparent.

---

## 4. Conversation memory is file-based

Conversation memory is stored in:

```text
memory/conversation.json
```

This is suitable for a simple local application.

For a production multi-user system, a database or dedicated session store would be more appropriate.

---

## 5. Conversation memory is currently global

The current backend maintains conversation memory at the application level.

This means multiple users using the same backend process could potentially share the same stored conversation history.

A production application should use separate sessions or user-specific memory.

---

## 6. No authentication

The FastAPI endpoints currently do not implement user authentication.

Before exposing the application publicly, authentication and authorization should be added.

---

## 7. ripgrep dependency

When running outside Docker, `rg` must be installed and available on the system `PATH`.

When running inside the backend Docker container, the backend Dockerfile should install ripgrep.

---

# Future improvements

Possible improvements include:

* Better keyword generation
* Query reformulation
* History-aware query reformulation
* Keyword optimization
* Semantic retrieval
* Hybrid keyword + semantic retrieval
* Search result ranking
* Better citation parsing
* Structured sources in API responses
* PDF/DOCX text sidecars
* Better document chunking
* Session-based conversation memory
* Database-backed memory
* User authentication
* User-specific knowledge bases
* Streaming responses
* Background document processing
* Health-check endpoints
* Production monitoring
* HTTPS
* Reverse proxy
* CI/CD
* Cloud deployment

---

# Project summary

GrepRAG is a lightweight RAG system designed around **ripgrep instead of vector search**.

The core idea is:

```text
User Question
      ↓
LLM generates search keywords
      ↓
grep_search()
      ↓
ripgrep searches documents
      ↓
Matching files and lines
      ↓
Context retrieval
      ↓
Expanded document context
      ↓
Gemini Agent
      ↓
Grounded answer
      ↓
File + line citations
```

The project combines:

```text
FastAPI
+
OpenAI Agents SDK
+
Google Gemini
+
ripgrep
+
Document Extraction
+
Conversation Memory
+
Streamlit
+
Docker
```

The result is a simple and explainable document question-answering system where the retrieval process can be inspected directly through the files, keywords, grep matches, context, logs, and citations.

The architecture can later be extended with semantic retrieval, better query reformulation, structured citations, session-based memory, authentication, and production deployment capabilities.
