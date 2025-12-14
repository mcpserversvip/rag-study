
# Proposal: Standardize Knowledge Base Miss Fallback

## Goal
Ensure the system provides a consistent, professional error message when the knowledge base contains no information relevant to the user's query.

## Changes
### RAG
#### [MODIFY] [prompt_templates.py](file:///Users/xiaoyubin/Desktop/mcpserversvip/rag-study/src/rag/prompt_templates.py)
- Update `MEDICAL_QA_TEMPLATE` to explicitly instruct the LLM to return a standard "No information found" message if the context is insufficient.
- Proposed message: "抱歉，知识库中暂时没有关于该问题的相关信息。"

## Verification
### Manual Verification
1.  Start the application.
2.  Ask a question known to be outside the knowledge base scope (e.g., "骨折怎么治疗").
3.  Verify the response is exactly the standard fallback message.
