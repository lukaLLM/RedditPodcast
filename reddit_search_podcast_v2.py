import asyncio
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum
import time

from asyncpraw.models.reddit.subreddit import Subreddit
import httpx
import asyncpraw
from dotenv import load_dotenv
from pydantic_ai import Agent
import logfire
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from telegram import Bot

# =============================================================================
# CONFIGURATION & SETUP

load_dotenv()

# Configure Logfire for debugging
logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
logfire.instrument_pydantic_ai()

# =============================================================================
# ENUMS FOR CONFIGURATION

class TimeFilter(Enum):
    """Reddit time filter options."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"

# Time filter for posts
TIME_FILTER = TimeFilter.DAY

# Subreddit configuration: {subreddit_name: post_limit}
SUBREDDIT_CONFIG = {
    "LocalLLaMA": 10,
    "artificial": 5,
    "MachineLearning": 2,
    "OpenAI": 2,
    "AI_Agents": 2,
    "ArtificialInteligence": 5
}

# SUBREDDIT_CONFIG = {
#     "LocalLLaMA": 10,
#     "artificial": 5,
#     "MachineLearning": 2,
#     "OpenAI": 2,
#     "AI_Agents": 2,
#     "ArtificialInteligence": 5
# }
TOP_COMMENTS_LIMIT = 10
REPLIES_PER_COMMENT = 5
LIMIT_FETCH_POSTS = 10

MODEL = "gemini-2.5-pro"

SYSTEM_PROMPT = """
You are a Reddit research analyst. Analyze the provided Reddit posts and comments based on specific criteria.

Your task:
1. Topic Analysis: Identify the most interesting topics based on user-specified criteria
2. Comments: Select the best comments that add value to the discussions of topics.
3. Key Insights: Extract notable insights and trends.
4. If you find conflicting opinions, highlight them.
5. Summarize your findings and provide only URL link to posts and aggregate insights so they are not repeated multiple times in the analysis. So the final analysis is as concise and informative as possible.
"""

USER_PROMPT = """
Look for most insightful posts and comments that would enrich my knowledge as AI Engineer. Look for New AI models, performance benchmarks, ideas for projects, novel ideas/techniques around AI. 
"""

# ====================================================================
# DATA MODELS

@dataclass
class AppDeps:
    """Dependencies container."""
    reddit_client: asyncpraw.Reddit
    http_client: httpx.AsyncClient

# =============================================================================
# TELEGRAM FUNCTIONS

async def send_telegram_message(message: str, parse_mode: str = "Markdown") -> bool:
    """Send a text message to Telegram."""
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            print("❌ Telegram credentials not configured")
            return False
        
        bot = Bot(token=bot_token)
        
        # Escape special characters for Markdown
        # Replace problematic characters that might cause parsing issues
        safe_message = message.replace("_", "\\_").replace("[", "\\[").replace("]", "\\]")
        
        await bot.send_message(
            chat_id=chat_id,
            text=safe_message,
            parse_mode=parse_mode
        )
        
        print(f"✅ Message sent to Telegram")
        return True
        
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        # Try sending without formatting as fallback
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=None
            )
            print(f"✅ Message sent (without formatting)")
            return True
        except:
            return False


async def send_telegram_document(file_path: str, caption: str = "") -> bool:
    """Send a document to Telegram."""
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            print("❌ Telegram credentials not configured")
            return False
        
        bot = Bot(token=bot_token)
        
        with open(file_path, 'rb') as f:
            await bot.send_document(
                chat_id=chat_id,
                document=f,
                caption=caption
            )
        
        print(f"✅ Document sent to Telegram: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending Telegram document: {e}")
        return False


# =============================================================================
# REDDIT FETCHING FUNCTIONS (Original code preserved)

async def fetch_top_posts_today(
    reddit_client: asyncpraw.Reddit,
    subreddit: str,
    limit: int = LIMIT_FETCH_POSTS,
    time_filter: TimeFilter = TimeFilter.DAY
) -> tuple[str, List[str]]:
    """Directly fetches top posts from a subreddit."""
    try:
        limit = min(limit, 10)
        print(f"\n🔍 Getting TOP posts from r/{subreddit} ({time_filter.value})...")

        subreddit_obj: Subreddit = await reddit_client.subreddit(subreddit)
        
        results = []
        urls = []
        post_count = 0

        async for post in subreddit_obj.top(time_filter=time_filter.value, limit=limit):
            post_count += 1
            
            content_preview = ""
            if post.selftext:
                content_preview = post.selftext[:300].replace("\n", " ")
                if len(post.selftext) > 300:
                    content_preview += "..."
            
            url = f"https://reddit.com{post.permalink}"
            urls.append(url)
            
            results.append({
                "title": post.title,
                "score": post.score,
                "comments": post.num_comments,
                "subreddit": post.subreddit.display_name,
                "url": url,
                "content_preview": content_preview
            })

            print(f"   ✓ {post.title[:70]}... ({post.score} ⬆️, {post.num_comments} 💬)")
        
        print(f"✅ Found {post_count} posts from r/{subreddit}\n")

        formatted = f"=== TOP POSTS from r/{subreddit} ({time_filter.value}) ===\n\n"
        
        for i, post in enumerate(results, 1):
            formatted += f"{i}. {post['title']}\n"
            formatted += f"   📍 r/{post['subreddit']} | "
            formatted += f"👍 {post['score']} upvotes | 💬 {post['comments']} comments\n"
            if post['content_preview']:
                formatted += f"   📝 {post['content_preview']}\n"
            formatted += f"   🔗 {post['url']}\n\n"
        
        return formatted.strip(), urls
        
    except Exception as e:
        return f"❌ Error getting posts from r/{subreddit}: {str(e)}", []


async def fetch_post_comments(
    reddit_client: asyncpraw.Reddit,
    post_url: str,
    top_comments_limit: int = TOP_COMMENTS_LIMIT,
    replies_per_comment: int = REPLIES_PER_COMMENT
) -> str:
    """Directly fetches a post with comments and replies."""
    try:
        top_comments_limit = min(top_comments_limit, 10)
        replies_per_comment = min(replies_per_comment, 5)
        
        submission = await reddit_client.submission(url=post_url)
        await submission.load()
        await submission.comments.replace_more(limit=1)
        
        top_level_comments = sorted(
            submission.comments, 
            key=lambda c: c.score, 
            reverse=True
        )[:top_comments_limit]
        
        comments_data = []
        
        for comment in top_level_comments:
            comment_text = comment.body[:500]
            if len(comment.body) > 500:
                comment_text += "..."
            
            replies_data = []
            if hasattr(comment, 'replies') and comment.replies:
                top_replies = sorted(
                    comment.replies,
                    key=lambda r: r.score if hasattr(r, 'score') else 0,
                    reverse=True
                )[:replies_per_comment]
                
                for reply in top_replies:
                    if hasattr(reply, 'body'):
                        reply_text = reply.body[:300]
                        if len(reply.body) > 300:
                            reply_text += "..."
                        
                        replies_data.append({
                            "score": reply.score,
                            "text": reply_text
                        })
            
            comments_data.append({
                "score": comment.score,
                "text": comment_text,
                "replies": replies_data
            })
        
        formatted = f"POST: {submission.title}\n"
        formatted += f"📍 r/{submission.subreddit.display_name} | "
        formatted += f"👍 {submission.score} upvotes | 💬 {submission.num_comments} comments\n"
        formatted += f"🔗 {post_url}\n"
        
        if submission.selftext:
            content = submission.selftext[:1000].replace("\n", " ")
            if len(submission.selftext) > 1000:
                content += "..."
            formatted += f"Post Content:\n{content}\n\n"
        
        formatted += f"TOP {len(comments_data)} COMMENTS\n\n"
        
        for i, comment in enumerate(comments_data, 1):
            formatted += f"{i}. ({comment['score']} ⬆️) {comment['text']}\n"
            
            if comment['replies']:
                formatted += f"   💬 Replies ({len(comment['replies'])}):\n"
                for j, reply in enumerate(comment['replies'], 1):
                    formatted += f"   {i}.{j}. ({reply['score']} ⬆️) {reply['text']}\n"
            formatted += "\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error fetching comments: {str(e)}"


# AI Agent
agent = Agent(
    MODEL,
    system_prompt=SYSTEM_PROMPT,
    deps_type=AppDeps
)


# =============================================================================
# OUTPUT HELPERS

def save_analysis_to_file(analysis: str, links: List[str]) -> str:
    """Saves AI analysis to timestamped file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reddit_analysis_{timestamp}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("🧠 AI ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Time Filter: {TIME_FILTER.value}\n")
            f.write(f"Model: {MODEL}\n")
            f.write(f"Posts Analyzed: {len(links)}\n")
            f.write(f"Subreddits: {list(SUBREDDIT_CONFIG.keys())}\n\n")
            
        
            f.write("USER CRITERIA:\n")
            f.write(USER_PROMPT + "\n\n")
            f.write("AI ANALYSIS:\n")
            f.write(analysis + "\n\n")
            f.write(f"📎 ANALYZED POSTS ({len(links)} total):\n")
            for i, link in enumerate(links, 1):
                f.write(f"{i}. {link}\n")
        
        return filename
        
    except IOError as e:
        print(f"❌ Failed to save analysis file: {e}")
        return None


# =============================================================================
# MAIN EXECUTION

async def main():
    """
    Complete workflow:
    1. Fetch Reddit posts and comments
    2. Generate AI analysis
    3. Save to file
    4. Send results to Telegram
    """
    
    required_vars = [
        "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET",
        "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        return
    
    print("🤖 REDDIT → AI ANALYSIS → NOTEBOOKLM PODCAST → TELEGRAM")
    print(f"⏰ Time Filter: {TIME_FILTER.value}")
    print(f"📊 Subreddits: {list(SUBREDDIT_CONFIG.keys())}\n")

    async with httpx.AsyncClient(timeout=300) as http_client:
        reddit_client = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="reddit-analyzer/3.0"
        )
        
        deps = AppDeps(reddit_client=reddit_client, http_client=http_client)
        
        try:
            # ========== STEP 1: FETCH REDDIT DATA ==========
            print("📝 STEP 1: Fetching Reddit posts...\n")
            
            all_posts_text = []
            all_links = []
            
            for subreddit_name, limit in SUBREDDIT_CONFIG.items():
                posts_text, urls = await fetch_top_posts_today(
                    reddit_client,
                    subreddit=subreddit_name,
                    limit=limit,
                    time_filter=TIME_FILTER
                )
                all_posts_text.append(posts_text)
                all_links.extend(urls)
            
            if not all_links:
                print("❌ No posts found!")
                return
            
            print(f"\n✅ Found {len(all_links)} posts\n")
            
            # ========== STEP 2: FETCH COMMENTS ==========
            print(f"📝 STEP 2: Fetching comments...\n")
            
            all_comments_text = []
            
            for i, link in enumerate(all_links, 1):
                print(f"[{i}/{len(all_links)}] {link}")
                comments_text = await fetch_post_comments(
                    reddit_client,
                    post_url=link,
                    top_comments_limit=10,
                    replies_per_comment=5
                )
                all_comments_text.append(comments_text)
                
                if i < len(all_links):
                    await asyncio.sleep(1)
            
            full_data = "\n\n".join(all_comments_text)
            print(f"\n✅ Comments fetched\n")
            
            # ========== STEP 3: AI ANALYSIS ==========
            print("🧠 STEP 3: Running AI analysis...\n")
            
            result = await agent.run(
                USER_PROMPT + f"\n\nAnalyze this Reddit data:\n{full_data}",
                deps=deps
            )
            
            analysis = result.output
            
            # Save analysis
            analysis_filename = save_analysis_to_file(analysis, all_links)
            print(f"💾 Analysis saved: {analysis_filename}\n")
            
            # ========== STEP 4: NOTEBOOKLM PODCAST ==========
            print("🎙️ STEP 4: Generating NotebookLM podcast...\n")
            
            credentials = get_google_credentials()
            if not credentials:
                print("⚠️ Skipping NotebookLM (credentials missing)")
                audio_url = None
            else:
                # Create notebook
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                notebook_name = await create_notebook(
                    http_client,
                    credentials,
                    f"Reddit AI Analysis - {timestamp}"
                )
                
                if notebook_name:
                    # Upload analysis as source
                    source_name = await upload_text_source(
                        http_client,
                        credentials,
                        notebook_name,
                        analysis,
                        "AI Analysis Report"
                    )
                    
                    if source_name:
                        # Generate audio
                        audio_data = await generate_audio_overview(
                            http_client,
                            credentials,
                            notebook_name
                        )
                        
                        audio_url = audio_data.get("downloadUri") if audio_data else None
                    else:
                        audio_url = None
                else:
                    audio_url = None
            
            # ========== STEP 5: SEND TO TELEGRAM ==========
            print("\n📱 STEP 5: Sending to Telegram...\n")
            
            # Prepare message
            message = f"🤖 *Reddit AI Analysis Complete*\n\n"
            message += f"📊 *Analyzed:* {len(all_links)} posts\n"
            message += f"📁 *Subreddits:* {', '.join(SUBREDDIT_CONFIG.keys())}\n"
            message += f"⏰ *Time Filter:* {TIME_FILTER.value}\n\n"
            
            if audio_url:
                message += f"🎙️ *Podcast:* [Listen on NotebookLM]({audio_url})\n\n"
            
            message += f"📄 *Analysis file attached below*"
            
            # Send message
            await send_telegram_message(message)
            
            # Send analysis file
            if analysis_filename:
                await send_telegram_document(
                    analysis_filename,
                    caption="📄 Full AI Analysis Report"
                )
            
            print("\n" + "="*60)
            print("✅ WORKFLOW COMPLETE!")
            print("="*60)
            print(f"📄 Analysis: {analysis_filename}")
            if audio_url:
                print(f"🎙️ Podcast: {audio_url}")
            print(f"📱 Sent to Telegram chat: {os.getenv('TELEGRAM_CHAT_ID')}")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error to Telegram
            await send_telegram_message(
                f"❌ *Error in Reddit Analysis*\n\n```{str(e)}```"
            )
            
        finally:
            await reddit_client.close()


if __name__ == "__main__":
    asyncio.run(main())