# 💻 Incident Resolution Agent (SRE Co-Pilot)

An autonomous, multi-agent RAG system built with **LangGraph**, **FAISS**, and **Streamlit** to slash MTTR by instantly troubleshooting production system outages using historical incident documentation and post-mortems.

---

##  Section 1: Project Overview

### The Business Problem
When a major IT system goes down (like an e-commerce checkout page crashing or a banking app freezing), every minute of downtime costs money and damages customer trust. IT support teams are instantly flooded with pressure. To fix the issue, engineers usually have to manually dig through messy Slack channels, old post-mortems, and hundreds of past tickets to see if this problem has happened before. This manual search is slow, exhausting, and prone to human error under stress.

### Why Companies Need This & How It Reduces MTTR
**MTTR** stands for *Mean Time To Resolution* (the average time it takes to fix a broken system). Companies desperately need to lower their MTTR. This AI Agent acts as an instant "brain" for the support team. Instead of an engineer spending two hours searching old files, the agent scans years of historical data in seconds, instantly matching the current live crash symptoms to a past incident.

### Cost Savings
System downtime can cost enterprise companies anywhere from **$5,600 to over $9,000 per minute**. By slashing the time it takes to find a solution from hours to minutes, this tool directly saves companies hundreds of thousands of dollars per outage.

### Value
* **High ROI:** It solves a real-world, multi-billion-dollar enterprise problem.
* **Advanced Tech Stack:** Most entries build simple sequential prompts. This project uses **LangGraph** to construct a structured, stateful multi-step agentic workflow that makes decisions dynamically.
* **Privacy & Cost Aware:** By utilizing **FAISS** and **Gemini's free tier** (or local Ollama), it proves that an enterprise can safely index internal logs securely without massive cloud bills.

---

### System Architecture Diagram

```mermaid
graph TD
    %% Styling Definitions
    classDef ui fill:#4A90E2,stroke:#1F4E79,stroke-width:2px,color:#fff;
    classDef core fill:#50E3C2,stroke:#1B7A63,stroke-width:2px,color:#000;
    classDef storage fill:#F5A623,stroke:#A05A00,stroke-width:2px,color:#fff;
    classDef engine fill:#B8E986,stroke:#558B2F,stroke-width:2px,color:#000;

    %% Components
    UI["💻 User Interface<br>(Streamlit Dashboard)"]:::ui
    Graph["🤖 AI Agent Core<br>(LangGraph State Machine)"]:::core
    FAISS["📦 Knowledge Base<br>(FAISS Vector Store)"]:::storage
    ST["✨ Sentence Transformers<br>(Local Embeddings)"]:::engine
    LLM["🧠 Reasoning Engine<br>(Gemini / Ollama)"]:::engine

    %% Step-by-Step Flow Pipeline
    UI -->|1. Submit Live Symptom| Graph
    Graph -->|2. Query Semantic Context| FAISS
    ST -->|3. Generate & Match Vectors| FAISS
    FAISS -->|4. Return Matched Chunks| Graph
    Graph -->|5. Evaluate & Synthesize| LLM
    LLM -->|6. Formulate Resolution Plan| Graph
    Graph -->|7. Display Analytics & RCA Report| UI

