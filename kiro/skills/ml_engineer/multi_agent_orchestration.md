---
id: multi_agent_orchestration
version: 1.0.0
owners: [ml_engineer]
tags: [multi-agent, langgraph, orchestration, tool-use, agentic, planner-executor, guardrails]
when_to_use: |
  When a single LLM call cannot complete the task: research + write + verify,
  or tasks requiring tool use (search, code execution, API calls).
  Multi-agent adds complexity -- only worth it when single-agent clearly fails.
inputs:
  - task_complexity, tool_types, error_recovery_needs, human_in_loop_points
outputs:
  - "agent_architecture: agent topology + tool definitions + loop design + guardrails"
---

# Multi-Agent Orchestration

> Single agent first. Multi-agent when: task requires more context than fits in one window,
> different steps need different capabilities, or parallelism would help.
> Every agent added multiplies failure modes.

## Patterns

- Planner -> Executor -> Verifier (sequential, most common)
- ReAct loop (think -> act -> observe -> think...) (single agent with tools)
- Parallel workers with aggregator (map-reduce style)
- Supervisor with specialists (routing to specialized sub-agents)

## ReAct single agent with tools (start here)

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    return serper.search(query)

@tool
def execute_python(code: str) -> str:
    """Execute Python code and return output. Use for calculations."""
    return sandbox.run(code, timeout=10)

llm = ChatOpenAI(model="gpt-4o", temperature=0)
agent = create_react_agent(llm, tools=[search_web, execute_python], prompt=react_prompt)
executor = AgentExecutor(agent=agent, tools=[search_web, execute_python], max_iterations=10)

result = executor.invoke({"input": "What is NVIDIA CAGR from 2020 to 2026?"})
```

## LangGraph for complex flows

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class ResearchState(TypedDict):
    query: str
    search_results: list
    draft: str
    critique: str
    iteration: int

def search_node(state: ResearchState) -> dict:
    return {"search_results": [search_web(state["query"])]}

def write_node(state: ResearchState) -> dict:
    draft = llm.invoke(f"Write a report based on: {state['search_results']}")
    return {"draft": draft.content, "iteration": state["iteration"] + 1}

def critique_node(state: ResearchState) -> dict:
    critique = llm.invoke(f"Critique this draft: {state['draft']}")
    return {"critique": critique.content}

def should_revise(state: ResearchState) -> str:
    if "APPROVED" in state["critique"] or state["iteration"] >= 3:
        return "done"
    return "revise"

graph = StateGraph(ResearchState)
graph.add_node("search", search_node)
graph.add_node("write", write_node)
graph.add_node("critique", critique_node)
graph.add_edge("search", "write")
graph.add_edge("write", "critique")
graph.add_conditional_edges("critique", should_revise, {"done": END, "revise": "write"})

app = graph.compile()
```

## Guardrails

```python
MAX_ITERATIONS = 10

def validated_tool_call(tool_fn, args):
    result = tool_fn(**args)
    if len(str(result)) > 10_000:
        return str(result)[:10_000] + "\n[TRUNCATED]"
    return result

HIGH_STAKES = ["delete", "send_email", "charge_payment", "deploy"]

def requires_approval(action: str) -> bool:
    return any(h in action.lower() for h in HIGH_STAKES)

import asyncio
async def run_with_timeout(agent, input_data, timeout=120):
    return await asyncio.wait_for(agent.ainvoke(input_data), timeout=timeout)
```

## Anti-patterns

- **Agents calling agents in unbounded loops**: always set max_iterations.
- **No tool output validation**: LLM passes unvalidated output to next tool -> prompt injection risk.
- **High-stakes actions without human approval**: agent sending emails or charging cards autonomously.
- **Too many tools**: more than 10 tools and LLM struggles to pick the right one.
- **No observability**: agentic traces need full logging to debug failures.

## Validation

- [ ] Max iteration limit set and tested (agent terminates, not loops infinitely).
- [ ] All tool outputs length-bounded before returning to agent.
- [ ] High-stakes tool calls require explicit human approval.
- [ ] Full traces logged (tool calls, outputs, reasoning steps).
- [ ] Tested with adversarial inputs (prompt injection via tool outputs).
