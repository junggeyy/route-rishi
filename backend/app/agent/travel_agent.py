from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from typing import List, Any

from app.agent.tool_definitions import all_tools
from app.core.config import settings

class TravelAgent:
    """
    Orchestrates the LLM and various tools to act as a travel planner.
    """
    def __init__(self, model_name="gemini-2.0-flash"):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.0,
            google_api_key=settings.GEMINI_API_KEY
        )
        self.tools = all_tools
        
        # prompt template for the agent; guides the LLM's behavior
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """You are a helpful and knowledgeable AI travel planner named Trava.
                 Your primary goal is to assist users in planning trips and answering travel-related questions by intelligently using the provided tools.
                 Always be friendly, concise, and helpful.

                 Here are some guidelines:
                 - When asked for flight, hotel, or weather information, ALWAYS use your tools. Do not make up information.
                 - If a tool requires information not provided by the user (e.g., specific dates for flights, check-in date for hotels), ask clarifying questions to get the necessary details.
                 - For flight searches, always ask for the number of adults if not specified.
                 - For hotel searches, always ask for check-in/out dates and number of adults if not specified.
                 - After using a tool, summarize the results clearly and concisely for the user.
                 - If a search yields no results, inform the user and suggest alternative criteria or dates.
                 - Be polite and provide a clear, easy-to-understand response.
                 - If a user asks for something outside your domain (e.g., booking tickets directly, personal advice), gracefully decline and redirect to travel planning.
                 """),
                MessagesPlaceholder(variable_name="chat_history"),
                MessagesPlaceholder(variable_name="tools"),
                MessagesPlaceholder(variable_name="tool_names"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # initiating the LangChain agent
        self.agent = create_structured_chat_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def run_query(
        self,
        user_query: str,
        chat_history: List[Any]= None
    ) -> str:
        """
        Runs a user query through the AI agent.
        Args:
            user_query (str): The user's input query.
            chat_history (List[Any]): Optional. A list of previous messages for conversational memory.
                                      Should be LangChain message objects (HumanMessage, AIMessage).
        Returns:
            str: The agent's response.
        """

        if chat_history is None:
            chat_history = []

        response = await self.agent_executor.ainvoke(
            {"input": user_query, "chat_history": chat_history}
        )

        return response["output"]
    
travel_agent = TravelAgent()
