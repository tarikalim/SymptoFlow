from backend.chatbot.load_data import load_documents
from backend.chatbot.agent.agent import Agent
import queue


class AgentPool:
    def __init__(self, pool_size=10):
        self.pool = queue.Queue(maxsize=pool_size)
        self.documents = load_documents()

        for _ in range(pool_size):
            self.pool.put(Agent(self.documents))

    def get_agent(self):
        return self.pool.get()

    def release_agent(self, agent):
        agent.chat_history = []
        self.pool.put(agent)


agent_pool = AgentPool(pool_size=2)