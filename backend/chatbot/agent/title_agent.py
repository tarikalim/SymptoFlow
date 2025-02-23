from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class TitleGenerator:
    def __init__(self, model="gpt-4o-mini", temperature=0.3):
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a chat title generator. Generate a concise, descriptive title (maximum 6-7 words) based on the first message in a conversation.
            Rules:
            - Keep it under 7 words
            - Be descriptive but concise
            - Capture the main topic/question
            - Remove any unnecessary words
            Example input: "What are the requirements for computer engineering department?"
            Example output: "Computer Engineering Department Requirements"
            """),
            ("human", "{message}")
        ])

    def generate_title(self, first_message: str) -> str:
        chain = self.prompt | self.llm
        result = chain.invoke({"message": first_message})
        return result.content