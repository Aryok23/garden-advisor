"""
Planner Module
Implements planning capability to break down complex queries
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class Planner:
    """Creates plans for handling user queries"""
    
    def __init__(self):
        self.plan_templates = {
            'weather_check': ['get_weather', 'analyze_watering_needs'],
            'plant_care': ['retrieve_plant_knowledge', 'provide_advice'],
            'reminder': ['parse_schedule', 'set_reminder'],
            'calculation': ['identify_calculation', 'execute_calculator'],
            'general': ['understand_query', 'retrieve_context', 'respond']
        }
        logger.info("Planner initialized")
    
    def create_plan(self, query: str, context: str = "") -> Dict:
        """Create a plan based on the query"""
        query_lower = query.lower()
        
        # Identify query type and create plan
        plan = {
            'query': query,
            'type': self._identify_query_type(query_lower),
            'steps': [],
            'requires_tools': False,
            'estimated_complexity': 'low'
        }
        
        # Determine steps based on query type
        if plan['type'] == 'weather_check':
            plan['steps'] = ['Check current weather', 'Analyze if watering is needed', 'Provide recommendation']
            plan['requires_tools'] = True
            plan['estimated_complexity'] = 'medium'
        
        elif plan['type'] == 'plant_care':
            plan['steps'] = ['Identify plant', 'Retrieve care knowledge from RAG', 'Provide personalized advice']
            plan['requires_tools'] = False
            plan['estimated_complexity'] = 'medium'
        
        elif plan['type'] == 'reminder':
            plan['steps'] = ['Parse schedule details', 'Create reminder', 'Confirm with user']
            plan['requires_tools'] = True
            plan['estimated_complexity'] = 'low'
        
        elif plan['type'] == 'calculation':
            plan['steps'] = ['Parse calculation request', 'Execute calculation', 'Explain result']
            plan['requires_tools'] = True
            plan['estimated_complexity'] = 'low'
        
        elif plan['type'] == 'search':
            plan['steps'] = ['Search for information', 'Summarize findings', 'Provide answer']
            plan['requires_tools'] = True
            plan['estimated_complexity'] = 'medium'
        
        else:  # general
            plan['steps'] = ['Understand query', 'Check memory for context', 'Provide helpful response']
            plan['requires_tools'] = False
            plan['estimated_complexity'] = 'low'
        
        logger.debug(f"Plan created for query type '{plan['type']}': {plan['steps']}")
        return plan
    
    def _identify_query_type(self, query: str) -> str:
        """Identify the type of query"""
        weather_keywords = ['weather', 'rain', 'temperature', 'forecast', 'should i water']
        plant_care_keywords = ['how to', 'care for', 'grow', 'plant', 'water frequency', 'sunlight']
        reminder_keywords = ['remind', 'schedule', 'set reminder', 'notify']
        calculation_keywords = ['calculate', 'how much', 'how many', 'liters', 'gallons']
        search_keywords = ['search', 'find', 'look up', 'information about']
        
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
            return 'general'
    
    def adjust_plan(self, plan: Dict, feedback: str) -> Dict:
        """Adjust plan based on feedback or errors"""
        # Simple plan adjustment logic
        if 'error' in feedback.lower() or 'failed' in feedback.lower():
            plan['steps'].append('Retry with alternative approach')
            plan['estimated_complexity'] = 'high'
        
        return plan