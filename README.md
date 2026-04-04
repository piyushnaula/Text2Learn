# Text2Learn 📚
**AI-Powered Course Generation Platform**

> Give it any topic -> get a full structured course with lessons, videos, and quizzes.

Built with `LangChain` · `LangGraph` · `LangSmith` · `RAG` · `Groq` · `MongoDB` · `Streamlit`

---

## How It Works

1. You type a topic (e.g. "Machine Learning Fundamentals")
2. AI generates **5 course units** — you review and confirm
3. AI generates **subtopics** for every unit — you review and confirm
4. You open any subtopic → AI agent searches the web and writes a full lesson
5. Watch an optional YouTube tutorial (only shown if highly relevant)
6. After finishing a unit → take the **unit quiz** (MCQ with explanations)
7. All content is cached — same subtopic never generated twice

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

---

## API Keys You Need

| Key | Where to Get |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) |
| `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) |
| `LANGCHAIN_API_KEY` | [smith.langchain.com](https://smith.langchain.com) |

---

## Project Structure

```
text2learn/                  
├── graph/
│   ├── course_graph.py            
│   └── nodes/
│       ├── generate_units.py      
│       ├── generate_subtopics.py  
│       ├── generate_content.py    
│       └── generate_quiz.py       
├── agents/
│   ├── content_agent.py           
│   └── tools/
│       ├── brave_tool.py          
│       ├── rag_tool.py            
│       └── youtube_tool.py        
├── rag/
│   ├── embedder.py                
│   └── retriever.py               
├── db/
│   ├── mongo.py                   
│   └── models.py                  
├── services/
│   ├── llm.py                     
│   └── quiz_service.py            
├── prompts/                       
│   ├── units_prompt.txt
│   ├── subtopics_prompt.txt
│   ├── content_prompt.txt
│   └── quiz_prompt.txt
├── .env  
├── app.py               
└── requirements.txt
```

---

## Settings (`.env`)

```env
SIMILARITY_THRESHOLD=0.85
VIDEO_RELEVANCE_THRESHOLD=0.75   
```

Increase `SIMILARITY_THRESHOLD` to be stricter (generate more fresh content).
Decrease it to reuse more cached content (faster and cheaper).

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| AI Orchestration | LangGraph |
| AI Chains + Agent | LangChain |
| Observability | LangSmith |
| LLM | Groq (llama-3.3-70b-versatile) |
| Web Search | Tavily Search API |
| Vector Cache | ChromaDB |
| Database | MongoDB |
| Embeddings | HuggingFace sentence-transformers |
| Video | YouTube Data API v3 |

---

## LangSmith Tracing

All LLM calls, agent steps, and tool uses are automatically traced in LangSmith.

View traces at [smith.langchain.com](https://smith.langchain.com).
