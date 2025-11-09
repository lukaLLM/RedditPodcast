"""
Main workflow that orchestrates Reddit fetching, AI analysis, and notifications.
"""
import os
from typing import Dict, List, Optional
import asyncpraw
import httpx
from dotenv import load_dotenv

from reddit_fetcher import fetch_all_reddit_data
from ai_analyzer import analyze_reddit_data
from telegram_sender import send_analysis_results, send_error_notification
from utils import save_analysis_to_file, validate_environment, save_email_data, save_llm_input
from tts_service import TTSInference
from email_fetcher import EmailFetcher

# Load environment variables
load_dotenv()


async def run_complete_workflow(
    subreddit_config: dict[str, int],
    time_filter: str,
    top_comments: int,
    replies_per_comment: int,
    model: str,
    system_prompt: str,
    user_prompt: str,
    send_to_telegram: bool = False,
    generate_tts: bool = False,
    tts_model: Optional[str] = None,
    voice_name: Optional[str] = None,
    tone_instructions: Optional[str] = None,
    fetch_emails: bool = False,
    email_address: Optional[str] = None,
    email_password: Optional[str] = None,
    allowed_senders: Optional[List[str]] = None,
    email_hours_back: int = 24,
    max_emails: int = 20,
    max_output_tokens: int = 8192,
    temperature: float = 1.0,
    top_p: float = 0.95,
    top_k: int = 64,
    thinking_budget: int = 8192  # ✅ Add
) -> tuple[str, str, Optional[str], Optional[str], Optional[str]]:
    """Complete workflow with optional email fetching."""
    
    print("🤖 REDDIT AI ANALYZER - WORKFLOW START")
    
    # Validate subreddit_config
    if not isinstance(subreddit_config, dict):
        error_msg = f"❌ subreddit_config must be a dict, got {type(subreddit_config)}"
        print(error_msg)
        return error_msg, None, None, None, None
    
    if not subreddit_config:
        error_msg = "❌ subreddit_config is empty"
        print(error_msg)
        return error_msg, None, None, None, None
    
    print(f"📊 Subreddits: {list(subreddit_config.keys())}")
    print(f"⏰ Time Filter: {time_filter}")
    
    # Validate environment
    is_valid, missing_vars = validate_environment()
    if not is_valid:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        print(f"❌ {error_msg}")
        return error_msg, None, None, None, None
    
    # Initialize clients
    async with httpx.AsyncClient(timeout=300) as http_client:
        reddit_client = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="reddit-analyzer/3.0"
        )
        
        try:
            # === STEP 1: FETCH REDDIT DATA ===
            print("\n📡 Fetching Reddit data...")
            reddit_data, raw_reddit_data = await fetch_all_reddit_data(
                reddit_client=reddit_client,
                subreddit_config=subreddit_config,
                time_filter=time_filter,
                top_comments=top_comments,
                replies_per_comment=replies_per_comment
            )
            
            if not reddit_data:
                raise ValueError("No posts found")
            
            print(f"✅ Fetched {len(raw_reddit_data)} characters of Reddit data")
            
            # === STEP 2: FETCH EMAILS (OPTIONAL) ===
            email_content = ""
            
            if fetch_emails and email_address and email_password and allowed_senders:
                print("\n📧 Fetching emails...")
                
                fetcher = EmailFetcher(
                    email_address=email_address,
                    password=email_password
                )
                
                emails = fetcher.fetch_emails(
                    allowed_senders=allowed_senders,
                    hours_back=email_hours_back,
                    max_emails=max_emails
                )
                
                if emails:
                    # Format emails for analysis (save later after run_folder is created)
                    email_content = fetcher.format_emails_for_analysis(
                        emails, 
                        max_length_per_email=10000
                    )
                    print(f"✅ Fetched {len(emails)} email(s)")
                else:
                    print("⚠️ No emails found")
                    emails = None
            else:
                emails = None
            
            # === STEP 3: ANALYZE WITH AI ===
            print("\n🤖 Analyzing with AI...")
            
            # Combine Reddit data with email content
            combined_content = raw_reddit_data
            if email_content:
                combined_content = f"{raw_reddit_data}\n\n---\n\n{email_content}"
                print(f"📧 Including {len(email_content)} characters of email content")
            
            # Run AI analysis
            analysis = await analyze_reddit_data(
                reddit_data=combined_content,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                reddit_client=reddit_client,
                http_client=http_client,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                thinking_budget=thinking_budget  # ✅ Add
            )
            
            if not analysis or len(analysis) < 100:
                raise ValueError("Analysis too short or empty")
            
            # === STEP 4: SAVE ALL FILES TO SINGLE RUN FOLDER ===
            # ✅ Save analysis first - this creates the run folder
            analysis_file, raw_data_file, run_folder = save_analysis_to_file(
                analysis=analysis,
                subreddit_config=subreddit_config,
                time_filter=time_filter,
                model=model,
                raw_reddit_data=raw_reddit_data
            )
            
            if not analysis_file or not raw_data_file:
                raise ValueError("Failed to save analysis files")
            
            print(f"📁 Run folder: {run_folder}")
            
            # ✅ Save LLM input to same run folder
            llm_input_file = save_llm_input(
                reddit_data=raw_reddit_data,
                email_data=email_content if email_content else None,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model,
                combined_content=combined_content,
                run_folder=run_folder
            )
            
            # ✅ Save email data to same run folder (if emails were fetched)
            email_data_file = None
            if emails:
                email_data_file = save_email_data(emails, run_folder=run_folder)
            
            # === STEP 5: GENERATE TTS (OPTIONAL) ===
            audio_file = None
            if generate_tts and tts_model and voice_name:
                try:
                    print("\n🎙️ Generating TTS audio...")
                    tts = TTSInference()  # ✅ Remove model parameter from init
                    audio_file = await tts.generate_audio(
                        model=tts_model,  # ✅ Pass model to generate_audio instead
                        text=analysis,
                        voice_name=voice_name,
                        tone_instructions=tone_instructions,
                        output_folder=str(run_folder)
                    )
                    print(f"✅ TTS audio generated")
                except Exception as e:
                    print(f"⚠️ Failed to generate TTS: {e}")
            
            # === STEP 6: SEND TO TELEGRAM (OPTIONAL) ===
            if send_to_telegram:
                print("\n📱 Sending results to Telegram...")
                num_posts = raw_reddit_data.count("LINK: https://reddit.com")
                telegram_success = await send_analysis_results(
                    analysis_file=analysis_file,
                    subreddit_config=subreddit_config,
                    time_filter=time_filter,
                    num_posts=num_posts,
                    audio_file=audio_file
                )
                
                if telegram_success:
                    print("✅ Results sent to Telegram")
                else:
                    print("⚠️ Failed to send to Telegram")
            
            print("\n✅ WORKFLOW COMPLETE!")
            print(f"📁 All files saved to: {run_folder}")
            
            return analysis_file, raw_data_file, audio_file, email_data_file, llm_input_file
            
        except Exception as e:
            error_msg = f"Error during workflow: {str(e)}"
            print(f"❌ {error_msg}")
            
            if send_to_telegram:
                await send_error_notification(error_msg)
            
            import traceback
            traceback.print_exc()
            
            return error_msg, None, None, None, None
            
        finally:
            await reddit_client.close()