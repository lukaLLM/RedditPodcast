"""
AI analysis using PydanticAI.
"""
import os
from dataclasses import dataclass
import asyncpraw
import httpx
from pydantic_ai import Agent
import logfire


# Configure Logfire
logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
logfire.instrument_pydantic_ai()


@dataclass
class AppDeps:
    """Dependencies container for AI agent."""
    reddit_client: asyncpraw.Reddit
    http_client: httpx.AsyncClient


async def analyze_reddit_data(
    reddit_data: str,
    user_prompt: str,
    system_prompt: str,
    model: str,
    reddit_client: asyncpraw.Reddit,
    http_client: httpx.AsyncClient
) -> str:
    """
    Analyze Reddit data using AI.
    
    Args:
        reddit_data: Formatted Reddit posts and comments
        user_prompt: User's analysis criteria
        system_prompt: System instructions for AI
        model: AI model to use
        reddit_client: Reddit client (for dependencies)
        http_client: HTTP client (for dependencies)
        
    Returns:
        str: AI analysis result
    """
    print("🧠 Running AI analysis...\n")
    
    # Create AI agent
    agent = Agent(
        model,
        system_prompt=system_prompt,
        deps_type=AppDeps
    )
    
    # Create dependencies
    deps = AppDeps(
        reddit_client=reddit_client,
        http_client=http_client
    )
    
    # Run analysis
    full_prompt = f"{user_prompt}\n\nAnalyze this Reddit data:\n{reddit_data}"
    
    result = await agent.run(full_prompt, deps=deps)
    
    analysis = result.output
    
    print("✅ AI analysis complete\n")
    
    return analysis