"""
Contact Agent — handles availability and contact questions.
"""
from langchain.prompts import ChatPromptTemplate
from backend.core.llm import get_llm

CONTACT_INFO = """
CHAIMA SAAD — Contact Information
Email: zidisaad.chaima@gmail.com
Phone: +33 758.949.591
GitHub: https://github.com/CSAADZIDI
Location: France
Driver's license: Yes (Permis B)
Languages: French (bilingual), English (professional), Arabic (native)
"""

CONTACT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", f"""You are Chaima SAAD speaking in first person about your own contact and availability.
Answer as if you are having a natural spoken conversation — warm, friendly, and direct.
Never use bullet points, lists, or headers. Write in flowing prose as you would speak out loud.
Keep answers to 2 sentences maximum. Be direct and stop after 2 sentences. Reply in the same language as the question.

{CONTACT_INFO}"""),
    ("human", "{question}"),
])


def answer_contact_question(question: str) -> str:
    llm = get_llm()
    chain = CONTACT_PROMPT | llm
    result = chain.invoke({"question": question})
    return result.content
