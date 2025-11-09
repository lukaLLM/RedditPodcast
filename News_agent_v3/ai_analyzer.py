"""
AI analysis using PydanticAI.
"""
import os
from dataclasses import dataclass
import asyncpraw
import httpx
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
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
    http_client: httpx.AsyncClient,
    max_output_tokens: int = 8192,
    temperature: float = 1.0,
    top_p: float = 0.95,
    top_k: int = 64,
    thinking_budget: int = 8192
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
        max_output_tokens: Maximum tokens in response
        temperature: Sampling temperature (0.0-2.0)
        top_p: Nucleus sampling threshold
        top_k: Top-k sampling value
        thinking_budget: Thinking tokens for Gemini reasoning (max 32768)
        
    Returns:
        str: AI analysis result
    """
    print("🧠 Running AI analysis...")
    print(f"⚙️ Model: {model}")
    print(f"⚙️ Config: max_tokens={max_output_tokens}, temp={temperature}, top_p={top_p}, top_k={top_k}, thinking={thinking_budget}\n")
    
    # Create dependencies
    deps = AppDeps(
        reddit_client=reddit_client,
        http_client=http_client
    )
    
    # Build model-specific configuration
    if model.startswith("gemini"):
        # Google Gemini - just generation parameters
        print("🤖 Using Google Gemini model")
        
        google_settings = GoogleModelSettings(
            temperature=temperature,
            max_tokens=max_output_tokens,
            top_p=top_p,
            top_k=top_k,
            google_thinking_config={'thinking_budget': thinking_budget}
        )
        
        google_model = GoogleModel(model)
        
        agent = Agent(
            google_model,
            system_prompt=system_prompt,
            deps_type=AppDeps,
            model_settings=google_settings
        )
        
    elif model.startswith("openai:"):
        # OpenAI models
        print("🤖 Using OpenAI model")
        
        openai_settings = ModelSettings(
            max_tokens=max_output_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        agent = Agent(
            model,
            system_prompt=system_prompt,
            deps_type=AppDeps,
            model_settings=openai_settings
        )
    
    else:
        raise ValueError(f"Unsupported model: {model}. Use 'gemini-*' or 'openai:*'")
    
    # Run analysis
    full_prompt = f"{user_prompt}\n\nAnalyze this Reddit data:\n{reddit_data}"
    
    result = await agent.run(full_prompt, deps=deps)
    analysis = result.output
    
    print("✅ AI analysis complete\n")
    
    return analysis