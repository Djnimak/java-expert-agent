from openai import OpenAI

from src.config import OPENAI_MODEL_NAME


def reflect_on_output(task_type: str, user_input: str, draft_output: str) -> str:
    """
    Reflect on the draft output and decide whether it should be kept or revised.

    task_type:
    - question_answering
    - code_generation
    - code_review
    """
    client = OpenAI()

    system_prompt = """
You are a self-reflection component for a Java Expert AI Agent.

Your task is to evaluate whether the draft output is good enough or should be revised.

You must evaluate based on:
- relevance to the user's request
- clarity
- completeness
- professionalism
- actionability
- correctness at a high level
- for code generation: readability, maintainability, Java best practices
- for code review: specificity, usefulness, and review quality
- for question answering: whether the answer is direct, clear, and appropriately scoped

Return your answer in exactly this format:

Decision: KEEP or REVISE
Reason: <short reason>
""".strip()

    user_prompt = f"""
Task type:
{task_type}

User input:
{user_input}

Draft output:
{draft_output}
""".strip()

    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content or ""


def should_revise(reflection_text: str) -> bool:
    return "Decision: REVISE" in reflection_text


def revise_output(task_type: str, user_input: str, draft_output: str, reflection_text: str) -> str:
    """
    Revise an existing output based on reflection feedback.
    """
    client = OpenAI()

    system_prompt = """
You are a Java Expert AI Agent improving your own previous output.

Revise the draft based on the reflection feedback.

Rules:
- Keep the same task intent.
- Improve clarity, completeness, structure, and professionalism.
- Do not add unnecessary fluff.
- Preserve the original source label if one exists.
- Return only the improved final output.
""".strip()

    user_prompt = f"""
Task type:
{task_type}

User input:
{user_input}

Current draft:
{draft_output}

Reflection feedback:
{reflection_text}

Please produce the improved final output.
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


def refine_with_reflection(task_type: str, user_input: str, draft_output: str) -> tuple[str, str]:
    """
    Run reflection and optionally revise the draft.
    Returns:
    - final_output
    - reflection_text
    """
    reflection_text = reflect_on_output(task_type, user_input, draft_output)

    if should_revise(reflection_text):
        revised_output = revise_output(task_type, user_input, draft_output, reflection_text)
        return revised_output, reflection_text

    return draft_output, reflection_text