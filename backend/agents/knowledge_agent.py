from agents.base_agent import BaseAgent
from rag.pipeline import RAGPipeline

class KnowledgeAgent(BaseAgent):
    def __init__(self):
        self.rag = RAGPipeline()

    async def run(self, query: str, context: dict) -> dict:
        result = await self.rag.answer(query)
        return result
