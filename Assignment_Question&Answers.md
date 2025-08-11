## Assignment: Questions & Answers

### ❓Question 1) What is the purpose of the `chunk_overlap` parameter when using `RecursiveCharacterTextSplitter` to prepare documents for RAG, and what trade-offs arise as you increase or decrease its value?

#### ✅Answer : Purpose and trade-offs of `chunk_overlap` in `RecursiveCharacterTextSplitter` :
- **Purpose**: chunk_overlap repeats a slice of text at the end of one chunk into the start of the next so information that crosses a boundary isn’t lost to retrieval.
- **Increase overlap**:
  - **Pros**: Higher chance of capturing boundary-spanning facts; can improve recall and answer completeness.
  - **Cons**: More duplicate content → larger index, higher embedding/storage/query cost, and more chances of retrieving redundant chunks (can hurt precision).
- **Decrease overlap**:
  - **Pros**: Smaller index and faster pipeline with less duplication.
  - **Cons**: Greater risk of chopping facts; may lower recall if key info falls on boundaries.
- Note: In this repo, `app/rag.py` currently uses `chunk_overlap=0` for simplicity and efficiency.
to minimize embedding time, memory, and latency, and to avoid redundant retrievals. This workshop repo prioritizes serving/graph orchestration speed over maximal recall, so we accept the slight recall trade-off.

### ❓Question 2) Your retriever is configured with search_kwargs={"k": 5}. How would adjusting k likely affect RAGAS metrics such as Context Precision and Context Recall in practice, and why?

#### ✅Answer : Effect of adjusting k on RAGAS Context Precision and Context Recall

In dense retrieval, `k` controls how many top-ranked chunks are returned for each query. In RAGAS, Context Recall measures whether the needed (gold) evidence appears in the retrieved context, while Context Precision measures how relevant the retrieved context is on average.

- Increase k (e.g., 5 → 10)
  - Context Recall: increases
    - Why: A larger candidate set raises the chance that gold evidence is included.
  - Context Precision: often decreases
    - Why: Lower-ranked items are typically less relevant or redundant, adding noise/duplicates.

- Decrease k (e.g., 5 → 3)
  - Context Recall: decreases
    - Why: A smaller set is more likely to miss some required evidence.
  - Context Precision: often increases
    - Why: Results focus on the most relevant chunks, reducing off-topic/duplicate content.

- Recommended settings
  - Recall gains from raising k usually show diminishing returns beyond a moderate range (≈5–10), while precision and cost/latency steadily worsen.
  - For broad/multi-fact queries or heterogeneous corpora, a higher k can be justified; otherwise keep k small and consider re-ranking/deduplication to preserve precision.

### ❓Question 3) Compare the agent and agent_helpful assistants defined in langgraph.json. Where does the helpfulness evaluator fit in the graph, and under what condition should execution route back to the agent vs. terminate?

#### ✅Answer : Compare `agent` vs `agent_helpful` and where the helpfulness evaluator fits
- **`agent` (maps to graph `simple_agent`)**: Model → tools when requested → model → end.
- **`agent_helpful` (maps to graph `agent_with_helpfulness`)**: Model → (tools if requested) → model → helpfulness evaluator → either loop back or end.

<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%;">
  <thead>
    <tr>
      <th>Aspect</th>
      <th>agent</th>
      <th>agent_helpful</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Assistant ID (langgraph.json)</td><td><code>agent</code></td><td><code>agent_helpful</code></td></tr>
    <tr><td>Graph ID</td><td><code>simple_agent</code></td><td><code>agent_with_helpfulness</code></td></tr>
    <tr><td>Module</td><td><code>app.graphs.simple_agent:graph</code></td><td><code>app.graphs.agent_with_helpfulness:graph</code></td></tr>
    <tr><td>Core nodes</td><td><code>agent</code>, <code>action</code> (ToolNode)</td><td><code>agent</code>, <code>action</code> (ToolNode), <code>helpfulness</code></td></tr>
    <tr><td>Base flow</td><td>agent → ToolNode (if tool_calls) → agent → END</td><td>agent → ToolNode (if tool_calls) → agent → helpfulness → (loop or END)</td></tr>
    <tr><td>Helpfulness evaluator</td><td>No</td><td>Yes</td></tr>
    <tr><td>When evaluator runs</td><td>N/A</td><td>After agent responds and no pending tool calls</td></tr>
    <tr><td>Routing condition</td><td>tool_calls? → <code>action</code>; else END</td><td><code>HELPFULNESS:Y</code> → END; <code>HELPFULNESS:N</code> → <code>agent</code></td></tr>
    <tr><td>Loop cap</td><td>N/A</td><td>Terminates on limit (<code>HELPFULNESS:END</code>)</td></tr>
    <tr><td>Purpose</td><td>Simple tool-using agent</td><td>Tool-using agent with post-response helpfulness check</td></tr>
  </tbody>
</table>

- **Where the helpfulness evaluator fits**: After the agent responds and there are no pending tool calls, execution routes to the helpfulness node. It checks if the answer is helpful (outputs `HELPFULNESS:Y` or `HELPFULNESS:N`).
- **Routing condition**:
  - If evaluator returns `Y` → terminate.
  - If `N` → route back to the agent to refine and try again (loop).
  - There is also a loop cap: if message history exceeds a limit, evaluator emits `HELPFULNESS:END` and the graph terminates.


