from openai import OpenAI

from src.config import OPENAI_MODEL_NAME


def build_context_from_chunks(retrieved_chunks: list[dict]) -> str:
    context_parts: list[str] = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f"""[Chunk {index}]
Source type: {chunk['source_type']}
File name: {chunk['file_name']}
Chunk index: {chunk['chunk_index']}
Similarity score: {chunk['score']}

Text:
{chunk['text']}
"""
        )

    return "\n\n".join(context_parts)


def ensure_source_label(answer_text: str, expected_label: str) -> str:
    """
    Ensure the final answer always starts with the expected source label.
    """
    cleaned = answer_text.strip()

    if cleaned.startswith(expected_label):
        return cleaned

    return f"{expected_label}\n\n{cleaned}"


def answer_from_internal_kb(question: str, context: str) -> str:
    client = OpenAI()

    system_prompt = """
You are a Java Expert AI Agent.

Answer using ONLY the provided internal knowledge base context.

Rules:
- Use only the provided context.
- Do not invent facts not supported by the context.
- If the answer is incomplete in the context, say so clearly.
- Be clear, professional, and concise.
- Do NOT include any source label yourself.
""".strip()

    user_prompt = f"""
Question:
{question}

Retrieved internal knowledge base context:
{context}
""".strip()

    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = response.choices[0].message.content or ""
    return ensure_source_label(answer, "Source: Internal knowledge base")


def answer_from_model_knowledge(question: str) -> str:
    client = OpenAI()

    system_prompt = """
You are a Java Expert AI Agent.

The internal knowledge base was not strong enough.
Answer from general model knowledge.

Rules:
- Be clear, professional, and concise.
- If you are uncertain, say so.
- Do NOT include any source label yourself.
- End with a line in this exact format:
Confidence: <number between 0.0 and 1.0>
""".strip()

    user_prompt = f"""
Answer this question from general Java/Spring/software knowledge:

{question}
""".strip()

    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content or ""


def answer_from_web_search(question: str) -> str:
    client = OpenAI()

    instructions = """
You are a Java Expert AI Agent.

Use web search to answer the question.

Rules:
- Be clear, professional, and concise.
- Explicitly mention that web search was used because the internal knowledge base and general model knowledge were not sufficient.
- Keep the answer short and focused.
- Do NOT include markdown links.
- Do NOT include any source label yourself.
""".strip()

    response = client.responses.create(
        model=OPENAI_MODEL_NAME,
        instructions=instructions,
        input=f"Answer this Java/Spring/software question using web search: {question}",
        tools=[{"type": "web_search_preview"}],
    )

    answer = response.output_text or ""
    return ensure_source_label(answer, "Source: Web search")


def generate_java_code(user_request: str) -> str:
    """
    Generate plain Java code based on the user's request.
    """
    client = OpenAI()

    system_prompt = """
You are a Java Expert AI Agent.

Generate plain Java code based on the user's request.

Rules:
- Start with: "Source: Generated using general Java best practices"
- Generate plain Java only, not Spring Boot code.
- Prefer clean, readable, maintainable code.
- Use professional naming.
- Add short comments only when they are genuinely helpful.
- After the code, provide a brief explanation of the design choices.
- If assumptions are needed, state them clearly.
""".strip()

    user_prompt = f"""
Generate Java code for this request:

{user_request}
""".strip()

    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content or ""


def review_java_code(user_request: str) -> str:
    """
    Review pasted Java code and provide professional PR-style comments.
    """
    client = OpenAI()

    system_prompt = """
You are a senior Java Tech Lead performing a professional code review.

Your task is to review the provided Java code and produce structured, actionable, professional feedback.

Review priorities:
- readability
- naming
- encapsulation
- maintainability
- separation of concerns
- error handling
- null-safety
- immutability where appropriate
- API design
- testability
- adherence to Java best practices

Rules:
- Start with: "Source: Code review based on provided Java code"
- Be constructive and professional.
- Avoid vague statements like "improve this" without explanation.
- If the code is acceptable, say what is good as well.
- Do not invent project context that was not provided.
- Format the answer with these sections exactly:

Summary
Strengths
Findings
Suggested improvements
Overall recommendation

- Under "Findings", use bullet points.
- For each finding, include:
  - Severity: High / Medium / Low
  - Issue
  - Why it matters
  - Recommendation
""".strip()

    user_prompt = f"""
Please review this Java code request:

{user_request}
""".strip()

    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content or ""


def generate_linkedin_post(user_request: str) -> str:
    """
    Generate a professional LinkedIn-style post in the agent's own voice.
    """
    client = OpenAI()

    system_prompt = """
You are the Java Expert AI Agent writing a LinkedIn post in your own voice.

The post must:
- explain what you do
- briefly explain how you were built
- mention that you were created as part of the Ciklum AI Academy
- include a mention of @Ciklum
- sound professional, authentic, and concise
- be 5 to 7 sentences long

Rules:
- Start with: "Source: Agent-generated LinkedIn post"
- Write in first person, as the agent itself.
- Do not use hashtags unless explicitly requested.
- Do not make the post too promotional or exaggerated.
- Keep it suitable for LinkedIn.
""".strip()

    user_prompt = f"""
Generate a LinkedIn post based on this request:

{user_request}
""".strip()

    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content or ""