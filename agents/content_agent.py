from pathlib import Path
from typing import Tuple
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from services.llm import llm_content
from agents.tools.tavily_tool import tavily_search
from agents.tools.rag_tool import rag_retrieval

REACT_PROMPT_TEMPLATE = """You are an expert teacher and researcher. Your job is to gather information and write a detailed lesson.

You have access to these tools:
{tools}

Tool names: {tool_names}

IMPORTANT RULES:
1. ALWAYS use rag_retrieval FIRST to check if the lesson already exists in cache.
2. If cache is found (CACHE HIT), use that content directly. Do NOT search the web.
3. If NO CACHE FOUND, use tavily_search to find information. Search 2-3 times with different queries to get full coverage.
4. After gathering enough information, write the final lesson in your Final Answer.

The lesson must follow this format in Final Answer:
- Start with a clear introduction
- Explain all key concepts with examples
- Use proper Markdown formatting (## headings, **bold**, bullet lists)
- End with "---SUMMARY---" followed by a 2-3 sentence plain-language summary

Use the following format STRICTLY:

Question: the input question you must answer
Thought: think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have enough information to write the lesson
Final Answer: [complete lesson in Markdown with ---SUMMARY--- at the end]

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

tools = [rag_retrieval, tavily_search]

react_prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)

agent = create_react_agent(
    llm=llm_content,
    tools=tools,
    prompt=react_prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=8,
    return_intermediate_steps=False,
)

def run_content_agent(subtopic, unit_title, topic):
    question = (
        f"Write a detailed lesson about '{subtopic}' "
        f"which is part of the unit '{unit_title}' "
        f"in a course about '{topic}'. "
        f"First check the RAG cache, then search the web if needed."
    )

    result = agent_executor.invoke({"input": question})
    full_response: str = result.get("output", "")

    if "---SUMMARY---" in full_response:
        parts = full_response.split("---SUMMARY---", 1)
        content = parts[0].strip()
        summary = parts[1].strip()
    else:
        content = full_response.strip()
        summary = content[:500] + "..." if len(content) > 500 else content

    return content, summary