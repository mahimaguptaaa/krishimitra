"""
TRUE MULTI-AGENT ORCHESTRATOR
Analyzes query → decides WHICH agents are needed → runs them in parallel → merges response.
"""
import asyncio
from services.llm_service import LLMService

PLAN_PROMPT = """
You are an orchestrator for an agricultural AI system.
Analyze the farmer's query and decide which agents are needed.

Available agents:
- WEATHER: rain, temperature, forecast, irrigation timing
- CROP_ADVICE: fertilizer, seeds, soil, irrigation methods, pest control
- DISEASE: crop disease, symptoms, plant health, treatment
- MARKET: mandi prices, where to sell, demand, market trends
- KNOWLEDGE: government schemes, general agriculture info from documents
- MEMORY: retrieve farmer profile, past conversations

Return a JSON list of required agent names ONLY. Example:
["WEATHER", "CROP_ADVICE"]

Query: {query}
"""

class OrchestratorV2:
    def __init__(self):
        self.llm = LLMService()

    async def _plan_agents(self, query: str, has_image: bool) -> list:
        if has_image:
            return ["DISEASE"]
        try:
            raw = self.llm.complete(PLAN_PROMPT.format(query=query))
            import json, re
            match = re.search(r"\[.*?\]", raw, re.DOTALL)
            agents = json.loads(match.group()) if match else ["CROP_ADVICE"]
            valid = {"WEATHER","CROP_ADVICE","DISEASE","MARKET","KNOWLEDGE","MEMORY"}
            return [a for a in agents if a in valid] or ["CROP_ADVICE"]
        except Exception:
            return ["CROP_ADVICE"]

    async def _run_agent(self, name: str, query: str, context: dict) -> dict:
        try:
            if name == "WEATHER":
                from agents.weather_agent import WeatherAgent
                return await WeatherAgent().run(query, context)
            elif name == "CROP_ADVICE":
                from agents.crop_advisor import CropAdvisorAgent
                return await CropAdvisorAgent().run(query, context)
            elif name == "DISEASE":
                from agents.disease_agent import DiseaseAgent
                return await DiseaseAgent().run(query, context)
            elif name == "MARKET":
                from agents.market_agent import MarketAgent
                return await MarketAgent().run(query, context)
            elif name == "KNOWLEDGE":
                from agents.knowledge_agent import KnowledgeAgent
                return await KnowledgeAgent().run(query, context)
            elif name == "MEMORY":
                from agents.memory_agent import MemoryAgent
                return await MemoryAgent().run(query, context)
        except Exception as e:
            return {"response": f"[{name} agent error: {e}]", "sources": []}

    async def route(self, query: str, context: dict) -> dict:
        needed = await self._plan_agents(query, bool(context.get("image_path")))

        # Run all needed agents in parallel
        tasks = [self._run_agent(name, query, context) for name in needed]
        results = await asyncio.gather(*tasks)

        if len(results) == 1:
            results[0]["agent_used"] = needed[0]
            results[0]["agents_consulted"] = needed
            return results[0]

        # Merge multiple agent responses
        combined = self._merge(query, needed, results)
        combined["agents_consulted"] = needed
        combined["agent_used"] = "+".join(needed)
        return combined

    def _merge(self, query: str, agents: list, results: list) -> dict:
        parts = []
        all_sources = []
        for agent, res in zip(agents, results):
            parts.append(f"[{agent}]:\n{res.get('response','')}")
            all_sources.extend(res.get("sources", []))

        combined_text = "\n\n".join(parts)
        merge_prompt = f"""
Multiple AI agents have analyzed a farmer's query. Synthesize their outputs into one clear, helpful answer.

Farmer Query: {query}

Agent Outputs:
{combined_text}

Write a single unified response. Be practical and specific. No bullet overload.
"""
        final = self.llm.complete(merge_prompt)
        return {"response": final, "sources": list(set(all_sources))}

# Backward compatibility
OrchestratorAgent = OrchestratorV2
