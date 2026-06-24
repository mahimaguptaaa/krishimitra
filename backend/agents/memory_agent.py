"""
MEMORY AGENT — retrieves and summarizes farmer profile for queries like
"What do you know about me?" or "What is my farm profile?"
"""
from agents.base_agent import BaseAgent
from services.llm_service import LLMService

class MemoryAgent(BaseAgent):
    def __init__(self):
        self.llm = LLMService()

    async def run(self, query: str, context: dict) -> dict:
        profile_text = f"""
Farmer Profile I have stored:
- Location: {context.get("state","Not recorded")}
- Crops: {", ".join(context.get("crops",[]) or ["Not recorded"])}
- Soil Type: {context.get("soil_type","Not recorded")}
- Land Area: {context.get("land_area_acres","Not recorded")} acres
- Irrigation: {context.get("irrigation_type","Not recorded")}
- Language: {context.get("farmer_language","Not recorded")}

Past Conversation:
{context.get("conversation_history","None yet")}
"""
        response = self.llm.complete(
            f"A farmer asked: \"{query}\"\n\n{profile_text}\n\n"
            "Respond helpfully telling them what you know about them and their farm."
        )
        return {"response": response, "sources": ["Farmer Memory System"]}
