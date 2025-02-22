from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from typing import List
from langchain_core.documents import Document


class Agent:
    def __init__(
            self,
            documents: List[Document],
            chat_model: str = "gpt-4o-mini",
            temperature: float = 0.3,
            embedding_model: str = "text-embedding-3-large",
    ):
        self.documents = documents
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self._temperature = temperature

        self.llm = ChatOpenAI(
            model=self.chat_model,
            temperature=self._temperature,
        )

        self.chat_history = []

        splitter = RecursiveCharacterTextSplitter()
        split_documents = splitter.split_documents(self.documents)

        embeddings = OpenAIEmbeddings(
            model=embedding_model,
        )
        vector_store = FAISS.from_documents(documents=split_documents, embedding=embeddings)
        self.document_retriever = vector_store.as_retriever(search_kwargs={"k": len(split_documents) // 5})

        self._build_prompt()
        self._build_tools()
        self._create_agent()

    def _build_prompt(self):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                You are a medical AI assistant specialized in supporting breast cancer patients and their doctors. Your responses must be strictly based on the patient’s medical records and general medical guidelines. You do not diagnose or prescribe medication but provide guidance based on available data.

                Core Responsibilities:
1. Personalize responses using the patient's medical records.
2. Provide evidence-based guidance and support for breast cancer patients.
3. If the necessary information is missing, encourage the patient to consult their doctor.
4. Maintain a compassionate and professional tone.

Response Protocol:
1. Analyze the patient’s historical records to provide informed responses.
2. If relevant data is available in the records, use it to guide the conversation.
3. If data is missing, explicitly state this and encourage the patient to update their records or consult their doctor.
4. Always maintain a patient-centric and empathetic approach.

Communication Style:
- Be supportive and understanding.
- Avoid making assumptions beyond the available records.
- Use simple and clear language suitable for patients.
- Provide step-by-step explanations when needed.
- Encourage communication with doctors for medical decisions.

                Documentation Priority:
                1. Always check  documentation first
                2. Only provide information that can be verified in the documents
                3. If documentation is unclear or unavailable, explicitly state this
                4. Direct users to official channels for clarification when needed

                """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    def _build_tools(self):
        document_retriever_tool = create_retriever_tool(
            self.document_retriever,
            "document_retriever_tool",
            "Use this tool to retrieve information about breast cancer, breast cancer treatments and breast cancer drugs.",
        )
        search_tool = TavilySearchResults()
        self.tools = [document_retriever_tool, search_tool]

    def _create_agent(self):
        self.agent = create_openai_functions_agent(llm=self.llm, prompt=self.prompt, tools=self.tools)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)

    def ask(self, question: str) -> str:
        response = self.agent_executor.invoke({"input": question, "chat_history": self.chat_history})["output"]
        self.chat_history.extend(
            [
                HumanMessage(content=question),
                AIMessage(content=response),
            ]
        )
        return response
