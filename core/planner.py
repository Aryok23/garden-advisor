"""
Planner Module (Hybrid Rule-based + LLM Fallback)
Breaks down complex or multilingual queries into executable plans.
"""

import os
import logging
from typing import Dict
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

# === Langchain / Groq setup ===
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

class Planner:
    """Hybrid Planner: Rule-based first, fallback to LLM if no match"""

    def __init__(self):
        try:
            self.llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model=os.getenv("GROQ_MODEL"),
                base_url=os.getenv("GROQ_API_BASE"),
            )
        except Exception as e:
            logger.warning(f"Groq LLM not initialized properly: {e}")
            self.llm = None

        self.plan_templates = {
            'weather_check': ['get_weather', 'analyze_watering_needs'],
            'plant_care': ['retrieve_plant_knowledge', 'provide_advice'],
            'reminder': ['parse_schedule', 'set_reminder'],
            'calculation': ['identify_calculation', 'execute_calculator'],
            'general': ['understand_query', 'retrieve_context', 'respond']
        }

        logger.info("Hybrid Planner initialized with Groq LLM fallback")

    # === MAIN ENTRY POINT ===
    def create_plan(self, query: str, context: str = "") -> Dict:
        """Create a plan based on the query (rule-based first, LLM fallback)"""
        query_lower = query.lower()

        # Step 1: Rule-based identification
        query_type = self._identify_query_type(query_lower)
        plan = {
            'query': query,
            'type': query_type,
            'steps': [],
            'requires_tools': False,
            'estimated_complexity': 'low'
        }

        # Step 2: Rule-based plan generation
        if query_type == 'weather_check':
            plan['steps'] = [
                'Check current weather',
                'Analyze if watering is needed',
                'Provide recommendation'
            ]
            plan['requires_tools'] = True
            plan['estimated_complexity'] = 'medium'

        elif query_type == 'plant_care':
            plan['steps'] = [
                'Identify plant',
                'Retrieve care knowledge from RAG',
                'Provide personalized advice'
            ]
            plan['requires_tools'] = False
            plan['estimated_complexity'] = 'medium'

        elif query_type == 'reminder':
            plan['steps'] = [
                'Parse schedule details',
                'Create reminder',
                'Confirm with user'
            ]
            plan['requires_tools'] = True
            plan['estimated_complexity'] = 'low'

        elif query_type == 'calculation':
            plan['steps'] = [
                'Parse calculation request',
                'Execute calculation',
                'Explain result'
            ]
            plan['requires_tools'] = True
            plan['estimated_complexity'] = 'low'

        elif query_type == 'search':
            plan['steps'] = [
                'Search for information',
                'Summarize findings',
                'Provide answer'
            ]
            plan['requires_tools'] = True
            plan['estimated_complexity'] = 'medium'

        else:
            # Step 3: If no match, fallback to LLM-based planner
            logger.warning(f"No rule matched for query: '{query}' → using LLM planner")
            plan = self._create_plan_with_llm(query, context)

        logger.debug(f"Plan created for query type '{plan['type']}': {plan['steps']}")
        return plan

    # === RULE-BASED DETECTION ===
    def _identify_query_type(self, query: str) -> str:
        """Identify query type (supports both English and Indonesian keywords)"""

        weather_keywords = [
            'weather', 'rain', 'temperature', 'forecast', 'should i water',
            'cuaca', 'hujan', 'suhu', 'prakiraan', 'apakah perlu menyiram'
        ]
        plant_care_keywords = [
            'how to', 'care for', 'grow', 'plant', 'sunlight',
            'cara merawat', 'tanam', 'menyiram', 'pupuk', 'tanaman'
        ]
        reminder_keywords = [
            'remind', 'schedule', 'set reminder', 'notify',
            'ingatkan', 'jadwal', 'pengingat', 'buat pengingat'
        ]
        calculation_keywords = [
            'calculate', 'how much', 'how many', 'liters', 'gallons',
            'hitung', 'berapa', 'jumlah', 'liter', 'galon'
        ]
        search_keywords = [
            'search', 'find', 'look up', 'information about',
            'cari', 'temukan', 'informasi tentang'
        ]

        if any(kw in query for kw in weather_keywords):
            return 'weather_check'
        elif any(kw in query for kw in reminder_keywords):
            return 'reminder'
        elif any(kw in query for kw in calculation_keywords):
            return 'calculation'
        elif any(kw in query for kw in search_keywords):
            return 'search'
        elif any(kw in query for kw in plant_care_keywords):
            return 'plant_care'
        else:
            return 'unknown'  # triggers LLM fallback

    # === LLM FALLBACK ===
    def _create_plan_with_llm(self, query: str, context: str = "") -> Dict:
        """Use Groq LLM to dynamically plan when rule-based match fails"""
        prompt = f"""
        You are a planning assistant for a smart chatbot.
        The user asked: "{query}"
        Context: {context}

        Your task:
        1. Understand the user's intent (in any language).
        2. Break the goal into 3-5 short, actionable steps.
        3. Return the plan in JSON format with these fields:
        - type: short label of the task
        - steps: list of steps
        - requires_tools: true/false
        - estimated_complexity: low/medium/high
        """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            text = response.content.strip()

            # Basic safe parse (expecting JSON-like)
            import json, re
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                parsed['query'] = query
                logger.info("Plan successfully generated by LLM")
                return parsed
            else:
                logger.warning("LLM did not return valid JSON, using fallback format")
                return {
                    'query': query,
                    'type': 'llm_generated',
                    'steps': [line.strip("- ") for line in text.split("\n") if line.strip()],
                    'requires_tools': False,
                    'estimated_complexity': 'medium'
                }

        except Exception as e:
            logger.error(f"LLM planning failed: {e}")
            return {
                'query': query,
                'type': 'fallback_general',
                'steps': ['Understand user query', 'Check memory/context', 'Generate helpful response'],
                'requires_tools': False,
                'estimated_complexity': 'low'
            }

    # === PLAN ADJUSTMENT ===
    def adjust_plan(self, plan: Dict, feedback: str) -> Dict:
        """Adjust plan based on feedback or errors"""
        if 'error' in feedback.lower() or 'failed' in feedback.lower():
            plan['steps'].append('Retry with alternative approach')
            plan['estimated_complexity'] = 'high'
        return plan