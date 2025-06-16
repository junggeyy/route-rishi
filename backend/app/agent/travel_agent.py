from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
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
                temperature=0.1,
                google_api_key=settings.GEMINI_API_KEY,
            )
            # wrapping tools to handle async/sync compatibility
            self.tools = all_tools

            # prompt template for the agent; guides the LLM's behavior
            self.prompt = PromptTemplate.from_template(
                """
                You are Trava, a helpful and knowledgeable AI travel planner. 
                Your primary goal is to assist users in planning trips and answering 
                travel-related questions by intelligently using the provided tools.

                IMPORTANT GUIDELINES:
                - When asked for flight, hotel, or weather information, ALWAYS use your tools. Never make up information.
                - Always call tools using a dictionary of arguments. Do NOT wrap it as a string.
                - If a tool requires information not provided by the user, ask clarifying questions first.
                - After using a tool, summarize the results clearly and concisely.
                - If a tool call/search yields no results or None, suggest alternative criteria or dates.
                - If a question can be answered directly without using any tools (e.g., greetings, philosophical questions, general knowledge), provide a 'Final Answer:' immediately, 
                without going through the Thought/Action/Observation cycle.
                - Be polite, helpful, and provide clear, easy-to-understand responses.
                
                TOOLS AVAILABLE:
                {tools}

                TOOL NAMES: {tool_names}

                Use the following format:

                Question: {input}
                Thought: [What do I need to do?]
                (if the answer can be directly provided without a tool, then end with Final Answer:
                Final Answer: the final answer to the original input question)
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action [tool result]
                ... (this Thought/Action/Action Input/Observation can repeat N times)
                Thought: I now know the final answer [What does this mean?]
                Final Answer: the final answer to the original input question [helpful response to user]

                Begin!

                Question: {input}
                Thought: {agent_scratchpad}
            """)

            # initiating the LangChain agent using ReAct pattern
            self.agent = create_react_agent(self.llm, self.tools, self.prompt)
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )

            logger.info("TravelAgent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize TravelAgent: {str(e)}")
            raise
    
    def run_query(
        self,
        user_query: str,
        chat_history: Optional[List[Any]]= None
    ) -> str:
        """
        Runs a user query through the AI agent.
        (synchronous version for testing)
        Args:
            user_query (str): The user's input query.
            chat_history (List[Any]): Optional. A list of previous messages for conversational memory.
        Returns:
            str: The agent's response.
        """
        try:
            response = self.agent_executor.invoke({"input": user_query, "agent_scratchpad": ""})
            return response["output"]

        except Exception as e:
            logger.error(f"Error in run_query: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or ask something else."
    
    async def run_query_async(
        self,
        user_query: str,
        chat_history: Optional[List[Any]]= None
    ) -> str:
        """
        Runs a user query through the AI agent.
        (asynchronous version)
        Args:
            user_query (str): The user's input query.
            chat_history (List[Any]): Optional. A list of previous messages for conversational memory.
        Returns:
            str: The agent's response.
        """
        try:
            response = await self.agent_executor.ainvoke({"input": user_query, "agent_scratchpad": ""})
            return response["output"]

        except Exception as e:
            logger.error(f"Error in run_query_async: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or ask something else."
    
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
