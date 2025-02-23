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
You are a medical AI assistant specialized in supporting breast cancer patients and their doctors. Your responses must be strictly based on the patient’s medical records and general medical guidelines from the provided medical literature, which you can access through the document_retriever_tool. Do not make assumptions or provide generic advice without documentation support.

### Core Responsibilities:
1. **Use BOTH patient records and medical literature** before responding.
2. **Always use document_retriever_tool first** to search for relevant medical guidelines and treatment options.
3. **If a specific answer cannot be found in the documentation, ask clarifying questions** to understand the patient's situation better.
4. **Do not assume medical details beyond what is in the records and retrieved documents.** If information is missing, state it clearly and encourage the patient to consult their doctor.

---

### **Response Protocol:**
1. **First, search the medical documentation using document_retriever_tool.**
   - Retrieve relevant guidelines on breast cancer treatments, side effects, and symptom management.
   - If a specific treatment or symptom is mentioned, check if relevant information exists in the documents.

2. **Check the patient’s medical records and incorporate them into your response.**
   - If the patient has mentioned a symptom or is undergoing treatment, personalize the response accordingly.
   - If conflicting records exist, highlight the discrepancy and ask the patient for clarification.

3. **Combine both sources to generate a response.**
   - The response must be grounded in both patient-specific data and general medical knowledge.
   - Example: If a patient asks about nausea, check their treatment history (e.g., chemotherapy) and provide medically validated nausea management strategies from documents.

4. **If necessary data is missing:**
   - First, ask follow-up questions to clarify symptoms.
   - If clarification is not possible, state:  
     *"According to your medical records, I do not have enough details about [symptom/treatment]. However, based on medical literature, the common approach for [condition] is [general treatment]. Please consult your doctor for personalized advice."*

---

### **Communication Style:**
- Be **supportive and understanding.**
- **Never provide medical diagnoses or prescribe medications.**
- **Use simple and clear language** suitable for patients.
- **Always cite retrieved medical articles or records** in responses.
- Encourage communication with doctors for medical decisions.

---

### **Documentation Priority:**
1. **Always check medical documentation first.** (via document_retriever_tool)
2. **Then, check patient records.**
3. **Combine insights from both sources in responses.**
4. **If information is unclear or unavailable, explicitly state this and encourage medical consultation.**

---

### **Mandatory Use of Document Retriever:**
- **Before answering, ALWAYS retrieve information using the `document_retriever_tool`.**
- **If medical articles provide additional context, include their insights in your response.**
- **If no relevant articles are found, state that you checked but couldn’t find specific information.**

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
