from openai import OpenAI

from src.config import OPENAI_MODEL_NAME


def classify_request(user_input: str) -> str:
    """
    Classify the user request into one of:
    - question_answering
    - code_generation
    - code_review
    """
    client = OpenAI()

    system_prompt = """
You are a request classifier for a Java Expert AI Agent.

Classify the user's request into exactly one of these labels:
- question_answering
- code_generation
- code_review

Definitions:
- question_answering: theoretical or explanatory questions about Java, Spring, design patterns, or software engineering concepts
- code_generation: requests to create, write, generate, or implement Java code
- code_review: requests to review, critique, improve, or comment on provided Java code

Rules:
- Return only one label.
- Do not explain your answer.
""".strip()

    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
    )

    label = (response.choices[0].message.content or "").strip()

    allowed = {"question_answering", "code_generation", "code_review"}
    if label not in allowed:
        return "question_answering"

    return label