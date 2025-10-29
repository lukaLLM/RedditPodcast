"""
Main workflow that orchestrates Reddit fetching, AI analysis, and notifications.
"""
import os
from typing import Dict, Optional
import asyncpraw
import httpx
from dotenv import load_dotenv

from reddit_fetcher import fetch_all_reddit_data
from ai_analyzer import analyze_reddit_data
from telegram_sender import send_analysis_results, send_error_notification
from utils import save_analysis_to_file, validate_environment

# Load environment variables
load_dotenv()


async def run_complete_workflow(
    subreddit_config: Dict[str, int],
    time_filter: str = "day",
    top_comments: int = 10,
    replies_per_comment: int = 5,
    model: str = "gemini-2.5-pro",
    system_prompt: str = "",
    user_prompt: str = "",
    send_to_telegram: bool = False
) -> tuple[str, str]:
    """
    Complete workflow: Fetch Reddit data → AI analysis → Save → Notify.
    
    Args:
        subreddit_config: Dict of {subreddit_name: post_limit}
        time_filter: Time period (hour, day, week, month, year, all)
        top_comments: Number of top comments per post
        replies_per_comment: Number of replies per comment
        model: AI model to use
        system_prompt: System instructions for AI
        user_prompt: User's analysis criteria
        send_to_telegram: Whether to send results to Telegram
        
    Returns:
        tuple: (path_to_analysis_file, path_to_raw_data_file) or (error_message, None)
    """
    
    print("="*80)
    print("🤖 REDDIT AI ANALYZER - WORKFLOW START")
    print("="*80)
    print(f"📊 Subreddits: {list(subreddit_config.keys())}")
    print(f"⏰ Time Filter: {time_filter}")
    print(f"🤖 Model: {model}")
    print(f"📱 Send to Telegram: {send_to_telegram}")
    
    # Validate environment
    is_valid, missing_vars = validate_environment()
    if not is_valid:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        print(f"❌ {error_msg}")
        return error_msg, None
    
    # Initialize clients
    async with httpx.AsyncClient(timeout=300) as http_client:
        reddit_client = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="reddit-analyzer/3.0"
        )
        
        try:
            # Step 1: Fetch Reddit data
            reddit_data, raw_reddit_data = await fetch_all_reddit_data(
                reddit_client=reddit_client,
                subreddit_config=subreddit_config,
                time_filter=time_filter,
                top_comments=top_comments,
                replies_per_comment=replies_per_comment
            )
            
            if not reddit_data:
                raise ValueError("No posts found")
            
            # Step 2: Run AI analysis
            analysis = await analyze_reddit_data(
                reddit_data=reddit_data,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                reddit_client=reddit_client,
                http_client=http_client
            )
            
            # Step 3: Save to files
            analysis_file, raw_data_file = save_analysis_to_file(
                analysis=analysis,
                subreddit_config=subreddit_config,
                time_filter=time_filter,
                model=model,
                raw_reddit_data=raw_reddit_data
            )
            
            if not analysis_file or not raw_data_file:
                raise ValueError("Failed to save files")
            
            # Step 4: Send to Telegram (if requested)
            if send_to_telegram:
                print("\n📱 Sending results to Telegram...\n")
                telegram_success = await send_analysis_results(
                    analysis_file=analysis_file,
                    subreddit_config=subreddit_config,
                    time_filter=time_filter,
                    num_posts=raw_reddit_data.count("LINK: https://reddit.com")
                )
                
                if telegram_success:
                    print("✅ Results sent to Telegram")
                else:
                    print("⚠️ Failed to send to Telegram")
            
            print("✅ WORKFLOW COMPLETE!")
            print(f"📄 Analysis saved: {analysis_file}")
            print(f"📊 Raw data saved: {raw_data_file}")
            if send_to_telegram:
                print(f"📱 Sent to Telegram: {os.getenv('TELEGRAM_CHAT_ID')}")
            
            return analysis_file, raw_data_file
            
        except Exception as e:
            error_msg = f"Error during workflow: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Send error to Telegram if enabled
            if send_to_telegram:
                await send_error_notification(error_msg)
            
            import traceback
            traceback.print_exc()
            
            return error_msg, None
            
        finally:
            await reddit_client.close()