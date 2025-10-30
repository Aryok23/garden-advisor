"""
Core Agent Implementation
Implements reasoning, planning, tool usage, and reflection
"""
import os
import logging
from typing import List
from openai import OpenAI

from core.memory import MemoryManager
from core.tools import ToolManager
from core.planner import Planner
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


logger = logging.getLogger(__name__)

class GardenAdvisorAgent:
    """Main LLM Agent with reasoning, planning, and reflection capabilities"""
    
    def __init__(self):
        # Initialize Groq client (compatible with OpenAI API)
        self.client = OpenAI(
            api_key=os.getenv('GROQ_API_KEY'),
            base_url=os.getenv('GROQ_API_BASE', 'https://api.groq.com/openai/v1')
        )
        self.model = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
        
        self.memory_manager = MemoryManager()
        self.tool_manager = ToolManager()
        self.planner = Planner()
        
        logger.info("Garden Advisor Agent initialized")
    
    def llm(self, messages):
        """Wrapper for LLM chat completions"""
        try:
            formatted_messages = [
                {"role": "system" if isinstance(m, SystemMessage) else
                        "user" if isinstance(m, HumanMessage) else
                        "assistant", "content": m.content}
                for m in messages
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=0.7
            )
            
            return AIMessage(content=completion.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM request failed: {e}", exc_info=True)
            return AIMessage(content="Sorry, I'm having trouble connecting to the LLM right now.")

    def _create_system_prompt(self) -> str:
        """Create system prompt with ReAct framework"""
        tools_description = self.tool_manager.get_tools_description()
        
        return f"""You are a Smart Garden Advisor Agent helping users with plant care.

    You use the ReAct (Reasoning + Acting) framework:
    1. Thought: Think about what you need to do
    2. Action: Choose a tool to use (if needed)
    3. Observation: Analyze the tool result
    4. Answer: Provide final response

    Available Tools:
    {tools_description}

    Guidelines:
    - Always think step-by-step
    - Use tools when you need specific information (weather, calculations, plant knowledge)
    - Be friendly and helpful
    - If you make a mistake, acknowledge and correct it
    - Remember user's previous conversations and their plants

    Format your response as:
    Thought: [your reasoning]
    Action: [tool_name: parameters] (if needed)
    Observation: [result analysis]
    Answer: [final response to user]
    """
    
    def _extract_action(self, response: str) -> tuple[str, str]:
        """Extract action from LLM response"""
        if "Action:" not in response:
            return None, None
        
        try:
            action_line = [line for line in response.split('\n') if line.strip().startswith('Action:')][0]
            action_content = action_line.split('Action:', 1)[1].strip()
            
            if ':' in action_content:
                tool_name, params = action_content.split(':', 1)
                return tool_name.strip(), params.strip()
        except Exception as e:
            logger.warning(f"Failed to extract action: {e}")
        
        return None, None
    
    def _reflect_on_response(self, user_query: str, response: str) -> str:
        """Reflection: Self-review and improve response, but return only final message"""
        reflection_prompt = f"""
    You are reviewing a chatbot's garden advice response.
    If the response is already good, keep it as is.
    If it can be improved, rewrite it in a clearer, more helpful, and friendly tone.

    Important:
    - Return **only the improved final message** for the user.
    - Do NOT include explanations, analysis, or lists of improvements.
    - Do NOT show reasoning or mention that it was improved.
    - Keep it natural, like a helpful assistant message.

    User Query: {user_query}
    Your Response: {response}

    Final improved message:
    """
    
        try:
            messages = [
                SystemMessage(content="You are a garden assistant response improver."),
                HumanMessage(content=reflection_prompt)
            ]
            
            reflection = self.llm(messages).content or response
            logger.info(f"Reflection completed for query: {user_query[:50]}")
            return reflection.strip()
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return response
    
    def process_message(self, user_id: str, message: str) -> str:
        """Main message processing with full agent capabilities"""
        logger.info(f"Processing message from user {user_id}: {message[:100]}")
        
        try:
            # 1. Load user memory
            conversation_history = self.memory_manager.get_short_term_memory(user_id)
            relevant_context = self.memory_manager.get_relevant_long_term_memory(user_id, message)
            
            # 2. Planning: Determine what needs to be done
            plan = self.planner.create_plan(message, relevant_context)
            logger.info(f"Plan created: {plan}")
            
            # 3. Reasoning: Build context with memory
            context_messages = [
                SystemMessage(content=self._create_system_prompt())
            ]
            
            # Add relevant long-term memory
            if relevant_context:
                context_msg = "Relevant context from past conversations:\n" + relevant_context
                context_messages.append(SystemMessage(content=context_msg))
            
            # Add conversation history (short-term memory)
            context_messages.extend(conversation_history)
            
            # Add current query
            context_messages.append(HumanMessage(content=message))
            
            # 4. Initial reasoning and action
            initial_response = self.llm(context_messages).content
            logger.info(f"Initial response: {initial_response[:200]}")
            
            # 5. Tool usage (if action detected)
            tool_name, tool_params = self._extract_action(initial_response)
            
            if tool_name:
                tool_result = self.tool_manager.execute_tool(tool_name, tool_params, user_id)
                logger.info(f"Tool {tool_name} executed: {tool_result[:100]}")
                
                # Add observation and generate final answer
                observation_msg = f"\nObservation: {tool_result}\n\nNow provide the final answer to the user."
                context_messages.append(AIMessage(content=initial_response))
                context_messages.append(HumanMessage(content=observation_msg))
                
                final_response = self.llm(context_messages).content
            else:
                final_response = initial_response
            
            # 6. Reflection: Self-review
            refined_response = self._reflect_on_response(message, final_response)
            
            # Extract clean answer
            if "Answer:" in refined_response:
                clean_answer = refined_response.split("Answer:", 1)[1].strip()
            else:
                clean_answer = refined_response
            
            # 7. Update memory
            self.memory_manager.add_to_short_term_memory(user_id, message, clean_answer)
            self.memory_manager.add_to_long_term_memory(user_id, message, clean_answer)
            
            logger.info(f"Response generated successfully for user {user_id}")
            return clean_answer
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    def get_user_plants(self, user_id: str) -> List[str]:
        """Get list of plants for a user"""
        return self.memory_manager.get_user_plants(user_id)
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up agent resources")