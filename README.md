# ⚡ DYNAMO

**Dynamic Network of Agents for Multi-Task Orchestration**

> Policy-selective adaptive multi-agent orchestration for financial deep research.

---

## 🚀 Setup (5 Minutes)

### 1. Get a Free Groq API Key

Get your API key from:

[Groq Console](https://console.groq.com?utm_source=chatgpt.com)

Free to get started — no credit card required.

---

### 2. Clone and Configure

```bash
git clone https://github.com/abhi-bhavsar/Dynamic-Network-of-Agent-for-Multi-Task-Orchestration-DYNAMO-.git

cd Dynamic-Network-of-Agent-for-Multi-Task-Orchestration-DYNAMO-

cp .env.example .env
```

Open `.env` and add your Groq API key:

```env
GROQ_API_KEY=your_api_key_here
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the Backend

Open **Terminal 1**:

```bash
uvicorn backend.main:app --reload --port 8000
```

---

### 5. Run the Frontend

Open **Terminal 2**:

```bash
streamlit run frontend/app.py --server.port 8501
```

---

### 6. Open in Your Browser

* **Streamlit UI:** `http://localhost:8501`
* **API Documentation:** `http://localhost:8000/docs`
* **Health Check:** `http://localhost:8000/health`

---

# 🧠 The Engineering Problem

Standard multi-agent frameworks often suffer from **compounded latency and token bloat**.

Passing the entire conversation history sequentially through every agent forces the LLM to repeatedly process redundant context, creating unnecessary computational overhead and bottlenecks.

DYNAMO addresses this by treating agent orchestration as an **adaptive distributed systems problem**.

Instead of activating every available agent for every query:

1. The incoming query is analyzed for complexity.
2. A policy is dynamically selected.
3. Only the necessary agents are spawned.
4. Agents execute concurrently using `asyncio`.
5. Each agent receives a tightly scoped memory slice instead of the entire context.
6. Results are synthesized into a final response.

---

# 🏗️ Architecture

```text
User Query
    ↓
[Feature Extraction]
    └── Computes F(Q) = (N, U, C, R)
    ↓
[PSE — Policy Selector]
    └── Φ(F(Q)) → Selects policy from Π
    ↓
[Meta-Orchestrator]
    └── LangGraph + Pydantic → SpawnManifest
    ↓
[Agent Execution]
    └── asyncio.gather() → Parallel ephemeral agents
    ↓
    Each agent receives M(aᵢ)
    └── Memory slice, not full context
    ↓
[Synthesis]
    └── Confidence-weighted merge
    ↓
Final Report
```

---

# 🎯 PSE Policy Space Π

The **Policy Selection Engine (PSE)** dynamically chooses an orchestration strategy based on extracted query features.

| Policy         | Trigger Condition       | Best For                    |
| -------------- | ----------------------- | --------------------------- |
| `ON_DEMAND`    | N ≥ 0.7, C ≤ 2, U < 0.6 | Novel, simple queries       |
| `POOL_BASED`   | N < 0.4, U ≥ 0.7        | Urgent, predictable queries |
| `PREDICTIVE`   | R ≥ 0.6, U < 0.7        | Recurring session patterns  |
| `HIERARCHICAL` | C ≥ 4, N ≥ 0.5          | Complex, novel research     |
| `COMPOSITE`    | Mixed signals           | Ambiguous query profiles    |

Where the feature representation is:

```text
F(Q) = (N, U, C, R)
```

representing the characteristics used by the policy-selection mechanism.

---

# 🔌 API Endpoints

| Method | Endpoint            | Description                                 |
| ------ | ------------------- | ------------------------------------------- |
| `GET`  | `/health`           | System health and Groq connection status    |
| `POST` | `/api/v1/query`     | Run the DYNAMO pipeline                     |
| `POST` | `/api/v1/benchmark` | Dynamic vs. static orchestration comparison |

---

# ⚡ Supported Groq Models

| Model                  | Speed     | Quality |
| ---------------------- | --------- | ------- |
| `llama-3.1-8b-instant` | ⚡ Fastest | Good    |
| `llama3-8b-8192`       | Fast      | Good    |
| `mixtral-8x7b-32768`   | Moderate  | Best    |

Change the model in your `.env` file:

```env
GROQ_MODEL=<model-name>
```

---

# 📊 Telemetry & Observability

DYNAMO includes a built-in benchmarking and observability system designed to empirically evaluate **token savings and latency reductions** compared with a static multi-agent baseline.

### 🐘 PostgreSQL Database

Every execution routed through the benchmark endpoint automatically calculates performance metrics and stores:

* Token counts
* Latency in milliseconds
* Selected orchestration policy
* Spawned agent configurations
* Performance deltas between static and dynamic execution

These results are logged in the:

```text
benchmark_runs
```

table for later analysis and visualization.

### 🔍 LangSmith Tracing

LangSmith tracing is integrated with the LangGraph state machine to provide granular visibility into:

* Node-by-node execution
* Individual agent execution times
* LLM/API bottlenecks
* Orchestration flow
* Agent-level performance characteristics

---

# 🐳 Docker Deployment

To provide a consistent environment across contributor machines and avoid local dependency or virtual-environment conflicts, DYNAMO supports full containerized deployment.

The stack includes:

* PostgreSQL
* FastAPI Backend
* Streamlit Frontend

### 1. Boot the Entire Stack

```bash
docker compose up --build -d
```

### 2. Initialize Database Tables

Run once after the first deployment:

```bash
docker compose exec backend python -m backend.core.init_db
```

### 3. View Live Execution Logs

```bash
docker compose logs -f
```

### 4. Shut Down the Environment

```bash
docker compose down
```

---

# 🧪 Evaluation Methodology

To reproduce benchmark evaluations:

1. Open the **Streamlit UI**.
2. Enable **Run Benchmark Mode** from the sidebar.
3. Submit a research query.
4. The system executes the **static baseline**, activating all five default agents sequentially.
5. The system executes the **dynamic DYNAMO pipeline**.
6. DYNAMO extracts query features and selects an appropriate PSE policy.
7. Only the required agents are spawned and executed concurrently.
8. The UI displays comparative optimization metrics.
9. Results are simultaneously committed to the local PostgreSQL database for export and further analysis.

The benchmark enables direct comparison between:

```text
Static Multi-Agent Pipeline
            VS
Dynamic Policy-Selective Orchestration
```

Key metrics include:

* Total latency
* Token consumption
* Number of activated agents
* Orchestration policy
* Performance improvement

---

# 📁 Project Structure

```text
dynamo/
├── backend/
│   ├── core/          ← Config, LLM client, PostgreSQL bridge
│   ├── pse/           ← Feature extractor, Policy selector
│   ├── orchestrator/  ← LangGraph state, nodes, graph
│   ├── agents/        ← Specialist agents
│   ├── memory/        ← Memory slicer
│   ├── synthesis/     ← Synthesis agent
│   ├── benchmark/     ← Static baseline + metrics
│   └── api/           ← FastAPI routes + schemas
│
├── frontend/
│   └── app.py         ← Streamlit UI
│
├── docker-compose.yml ← Multi-container orchestration
├── .env.example
├── requirements.txt
└── README.md
```

---

# 🔬 Core Idea

DYNAMO explores a simple but important question:

> **Why should every query activate the same static pipeline of agents?**

Instead of relying on a fixed workflow, DYNAMO dynamically determines:

```text
Query Characteristics
        ↓
Policy Selection
        ↓
Required Agent Configuration
        ↓
Parallel Execution
        ↓
Scoped Memory
        ↓
Confidence-Weighted Synthesis
```

The goal is to reduce:

* 🔻 Unnecessary token consumption
* 🔻 Redundant context propagation
* 🔻 Agent activation overhead
* 🔻 Sequential execution latency

while maintaining the capability to handle complex research tasks through adaptive orchestration.

---

# ⚙️ Technology Stack

* **Python**
* **FastAPI**
* **Streamlit**
* **LangGraph**
* **Pydantic**
* **Groq**
* **PostgreSQL**
* **Docker**
* **Asyncio**

---

# 🚀 DYNAMO

**Dynamic orchestration. Selective computation. Adaptive multi-agent systems.**
