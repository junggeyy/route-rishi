from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory

from typing import List, Any, Dict, Optional
import logging

from app.agent.tool_definitions import all_tools
from app.core.config import settings
from app.agent.prompts import get_full_system_prompt

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
            system_prompt = SystemMessagePromptTemplate.from_template(get_full_system_prompt())
            self.prompt = ChatPromptTemplate.from_messages([
                system_prompt,
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
