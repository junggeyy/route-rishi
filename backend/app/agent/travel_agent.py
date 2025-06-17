from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

from typing import List, Any, Dict, Optional
import logging

from app.agent.tool_definitions import all_tools
from app.core.config import settings

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelAgent:
    """
    Orchestrates the LLM and various tools to act as a travel planner.
    """
    def __init__(self, model_name="gemini-2.0-flash"):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.3,
                google_api_key=settings.GEMINI_API_KEY,
            )
            self.tools = all_tools

            self.conversations = {}

            # prompt template for the agent; guides the LLM's behavior
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """
                You are Trava, an enthusiastic and knowledgeable AI travel companion! 
                
                YOUR PERSONALITY:
                - You're passionate about travel and genuinely excited to help people explore the world
                - You speak naturally and conversationally, like a knowledgeable friend who loves to travel
                - You sometimes use emojis appropriately to add warmth and excitement
                - You're encouraging and help users get excited about their travel plans
                - You ask questions in a friendly, curious way rather than being robotic
                
                CORE PRINCIPLES:
                1. Always be helpful and enthusiastic - Travel planning should be fun!
                2. Use tools when needed - For flights, hotels, weather, currency, and dates, ALWAYS use your tools
                3. Ask smart questions - When you need information, explain why it helps create a better experience
                4. Provide context - Use place information to enrich your responses
                5. Think step by step - For complex itineraries, break things down logically
                
                WHEN TO USE TOOLS:
                - Date tool: Anytime the exact year, month is not provided or when the users mention "today", "tomorrow", "next week", "this weekend", etc.
                - Weather tool: For any weather-related questions or when planning outdoor activities
                - Flight tool: For flight searches, prices, or travel logistics
                - Hotel tool: For accommodation searches and recommendations
                - Currency tool: For budget planning or cost comparisons
                
                CONVERSATION FLOW:
                1. Greet warmly and understand what they want to do
                2. Ask for missing information in a friendly way, explaining why you need it
                3. Use tools to gather real-time information
                4. Provide comprehensive responses with practical details and excitement
                5. Offer additional suggestions based on the place, time to enhance their trip
                
                FOR COMPREHENSIVE ITINERARY REQUESTS:
                When someone asks for a complete trip plan, follow this structure:
                1. Clarify the basics: Dates, budget, travel style, group size
                2. Get weather info when possible to inform activity suggestions
                3. Search flights to understand travel costs and timing
                4. Find accommodations that match their style and budget
                5. Suggest activities based on the destination and weather
                6. Provide practical tips: Currency, local customs, transportation
                7. Create a day-by-day breakdown if they want detailed planning
                
                HANDLING ERRORS:
                - If a tool returns no results, suggest alternatives
                - If information is unclear, ask for clarification in a helpful way
                - Always try to be solution-oriented
                
                Remember: You're not just providing information - you're helping create amazing travel memories! 🎒✨
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            # initiating the LangChain agent using ReAct pattern
            self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,
                return_intermediate_steps=True,
            )

            logger.info("TravelAgent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize TravelAgent: {str(e)}")
            raise
    
    def run_query(
        self,
        user_query: str,
        conversation_id: str
    ) -> str:
        """
        Runs a user query through the AI agent.
        (synchronous version for testing)
        Args:
            user_query (str): The user's input query.
            conversation_id (str):  Unique conversation id.
        Returns:
            str: The agent's response.
        """
        # gets the history for this conversation, or creates a new one if it's the first message.
        chat_history = self.conversations.setdefault(conversation_id, ChatMessageHistory())

        try:
            response = self.agent_executor.invoke({"input": user_query,  "chat_history": chat_history.messages})
            
            # update the history with the latest exchange.
            chat_history.add_user_message(user_query)
            chat_history.add_ai_message(response["output"])

            return response["output"]

        except Exception as e:
            logger.error(f"\nError in run_query: {str(e)}")
            return f"I encountered an error while processing your request. Please try rephrasing your question or ask something else."
    
    async def run_query_async(
        self,
        user_query: str,
        conversation_id: str   
    ) -> str:
        """
        Runs a user query through the AI agent.
        (asynchronous version)
        Args:
            user_query (str): The user's input query.
            conversation_id (str):  Unique conversation id.
        Returns:
            str: The agent's response.
        """
        # gets the history for this conversation, or creates a new one if it's the first message.
        chat_history = self.conversations.setdefault(conversation_id, ChatMessageHistory())
        try:
            response = await self.agent_executor.ainvoke({"input": user_query,  "chat_history": chat_history.messages})
            
            # update the history with the latest exchange.
            chat_history.add_user_message(user_query)
            chat_history.add_ai_message(response["output"])
            
            return response["output"]

        except Exception as e:
            logger.error(f"\nError in run_query_async: {str(e)}")
            return f"I encountered an error while processing your request. Please try rephrasing your question or ask something else."
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the agent and tools.
        """
        try:
            # test basic LLM connection
            test_response = self.llm.invoke("Hello")
            
            return {
                "status": "healthy",
                "llm_model": self.llm.model,
                "available_tools": [tool.name for tool in self.tools],
                "tools_count": len(self.tools)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "tools_count": len(self.tools)
            }

travel_agent = TravelAgent()
