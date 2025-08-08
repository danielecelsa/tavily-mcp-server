from mcp.server.fastmcp import FastMCP
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
from fastapi import FastAPI
from contextlib import AsyncExitStack, asynccontextmanager
import os

if os.getenv("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

mcp = FastMCP(name="TavilyServer", host="0.0.0.0", port=10000, stateless_http=True, lifespan=None)

if "TAVILY_API_KEY" not in os.environ:
    raise Exception("TAVILY_API_KEY environment variable not set")
  
# Tavily API key
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]

# Initialize Tavily client
tavily_client = TavilyClient(TAVILY_API_KEY)

@mcp.tool()
def web_search(query: str) -> str:
    """
    Use this tool to search the web for information.

    Args:
        query: The search query.

    Returns:
        A summary of the results.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    try:
        response = tavily_client.search(query, limit=3)
        results = [item["content"] for item in response["results"]]
        if not results:
            return "No results found."
        # Generate a summary of the results using the LLM
        summary = "\n\n".join(results)
        prompt = f"Briefly summarize these passages:\n\n{summary}"
        out = llm.invoke(prompt)
        return out.content.strip()
    except tavily_client.TavilyError as e:
        raise RuntimeError(f"Tavily search failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Web search failed: {e}")

#if __name__ == "__main__":
#    mcp.run(transport="streamable-http")


#@asynccontextmanager
#async def lifespan(app: FastAPI):
#    async with mcp.session_manager.run():
#        yield

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        # Questo avvia il session_manager solo per il tool MCP
        await stack.enter_async_context(mcp.session_manager.run())
        yield

app = FastAPI(lifespan=lifespan)
app.mount("/tav", mcp.streamable_http_app())