from langchain_groq import ChatGroq
import asyncio
from dotenv import load_dotenv
from mcp_use import MCPAgent, MCPClient
import os

async def run_memory_chat():
    load_dotenv()
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    config_file = "server/weather.json"

    print("Initializing chat...")

    client = MCPClient.from_config_file(config_file)
    llm = ChatGroq(model="qwen-qwq-32b")
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,
    )

    print("\n------ Interactive MCP Client ------\n")
    print("Type 'exit' to quit\n")
    print("Type 'clear' to clear the conversation history\n")
    print("-------------------------------------------\n")

    try:
        while True:
            user_input = input("You: ")

            if user_input.lower() == "exit":
                print("Exiting...")
                break
            elif user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue
            
            print("\nAssistant: ",end="",flush=True)
            try:
                response = await agent.run(user_input)
                print(response)
            except Exception as e:
                print("\n Error: {e}")
            
            finally:
                if client and client.sessions:
                    await client.close_all_sessions()
    except Exception as e:
        print(f"Error: {e}")
        await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_memory_chat())