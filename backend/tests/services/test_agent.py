import asyncio
import uuid
from app.agent.travel_agent import travel_agent
from datetime import date, timedelta

from app.core.config import settings
print("Gemini API Key loaded:", bool(settings.GEMINI_API_KEY))

async def main():
    session_id = str(uuid.uuid4())
    print(f"Starting new chat with session ID: {session_id}\n")
    
    print("Welcome to the RouteRishi Agent Playground!")
    print("Try asking questions like:")
    print("- What's the weather in Paris tomorrow?")
    print("- How much is 1 USD in Euros?")
    print("- Find flights from JFK to CDG for 1 adult on 2025-07-20.")
    print("- Find hotels in London for 2 adults checking in on 2025-08-01 and checking out 2025-08-05.")
    print("-" * 30)

    # # Example 1: Weather query
    # query1 = "What's the weather like in New York today?"
    # print(f"\nUser: {query1}")
    # response1 = await travel_agent.run_query_async(query1)
    # print(f"Trava: {response1}")

    # # Example 2: Flight query (ensure dates are in the future for test API)
    # departure_date_str = (date.today() + timedelta(days=30)).isoformat() # 30 days from now
    # return_date_str = (date.today() + timedelta(days=35)).isoformat() # 35 days from now
    # query2 = f"Find non-stop flights from JFK to PAR for 2 adults on {departure_date_str} returning {return_date_str}, max price $3000."
    # print(f"\nUser: {query2}")
    # response2 = await travel_agent.run_query_async(query2)
    # print(f"Trava: {response2}")

    # # Example 3: Hotel Query (ensure dates are in the future)
    # check_in_date_str = (date.today() + timedelta(days=30)).isoformat()
    # check_out_date_str = (date.today() + timedelta(days=35)).isoformat()
    # query3 = f"Find a 4-star hotel in Rome for 1 adult checking in on {check_in_date_str} and checking out on {check_out_date_str}."
    # print(f"\nUser: {query3}")
    # response3 = await travel_agent.run_query_async(query3)
    # print(f"Trava: {response3}")

    # # Example 4: Currency query
    # query4 = "How many Japanese Yen can I get for 1 US Dollar?"
    # print(f"\nUser: {query4}")
    # response4 = await travel_agent.run_query_async(query4)
    # print(f"Trava: {response4}")

    print("\n--- Interactive Session ---")
    while True:
        user_input = input("\nUser (type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        agent_response = await travel_agent.run_query_async(user_input, session_id)
        print(f"Trava: {agent_response}")

if __name__ == "__main__":
    asyncio.run(main())