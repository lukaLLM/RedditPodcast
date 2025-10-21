import asyncio
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List
from enum import Enum

from asyncpraw.models.reddit.subreddit import Subreddit
import httpx
import asyncpraw
from dotenv import load_dotenv
from pydantic_ai import Agent
import logfire

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
TIME_FILTER = TimeFilter.DAY  # Change to TimeFilter.WEEK, TimeFilter.MONTH, etc.

# Subreddit configuration: {subreddit_name: post_limit}
SUBREDDIT_CONFIG = {
    "LocalLLaMA": 10,
    "artificial": 5,
    "MachineLearning": 2,
    "OpenAI": 2,
    "AI_Agents": 2,
    "ArtificialInteligence":5
}

TOP_COMMENTS_LIMIT = 10
REPLIES_PER_COMMENT = 5
LIMIT_FETCH_POSTS = 10

MODEL="gemini-2.5-pro"

SYSTEM_PROMPT="""
        You are a Reddit research analyst. Analyze the provided Reddit posts and comments based on specific criteria.
        
        Your task:
        1. Topic Analysis: Identify the most interesting topics based on user-specified criteria
        2. Comments: Select the best comments that add value to the discussions of topics.
        3. Key Insights: Extract notable insights and trends.
        4. If you find conflicting opinions, highlight them.
        5. Summarize your findings and provide only URL link to posts and aggregate insights so they are not repeated multiple times in the analysis. So the final analysis is as concise and informative as possible.

        """

USER_PROMPT= """
Look for most insightful posts and comments that would enrich my knowledge as AI Enginner. Look for New AI models, performance benchmarks, ideas for projects, novel ideas/techniques around AI. 
"""

# ====================================================================
# DATA MODELS

@dataclass
class AppDeps:
    """Dependencies container."""
    reddit_client: asyncpraw.Reddit
    http_client: httpx.AsyncClient


# =============================================================================
# REDDIT FETCHING FUNCTIONS (No LLM, just direct API calls)

async def fetch_top_posts_today(
    reddit_client: asyncpraw.Reddit,
    subreddit: str,
    limit: int = LIMIT_FETCH_POSTS,
    time_filter: TimeFilter = TimeFilter.DAY
) -> tuple[str, List[str]]:
    """
    Directly fetches top posts from a subreddit.
    
    Args:
        reddit_client: AsyncPRAW Reddit client
        subreddit: Subreddit name
        limit: Maximum number of posts
        time_filter: Time period (hour, day, week, month, year, all)
    
    Returns:
        Tuple of (formatted_text, list_of_urls)
    """
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
    """
    Directly fetches a post with comments and replies.
    """
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
        
        # Format output
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


# Uncomment and modify the agent section
agent = Agent(
    MODEL,
    system_prompt=(
        SYSTEM_PROMPT
    ),
    deps_type=AppDeps
)

# =============================================================================
# OUTPUT HELPERS

def extract_reddit_links(text: str) -> List[str]:
    """Extracts all Reddit URLs from text."""
    return re.findall(r'https://(?:www\.)?reddit\.com[^\s\)]+', text)


def save_data_to_file(all_data: str, links: List[str]) -> str:
    """Saves raw data to timestamped file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reddit_data_{timestamp}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("REDDIT POSTS & COMMENTS DATA\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Time Filter: {TIME_FILTER.value}\n")
     
            f.write(all_data)
            
            if links:
                f.write(f"📎 ALL REDDIT LINKS ({len(links)} posts)\n")
                for i, link in enumerate(links, 1):
                    f.write(f"{i}. {link}\n")
        
        return filename
        
    except IOError as e:
        print(f"❌ Failed to save file: {e}")
        return None


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
            f.write(f"Subreddits: {list(SUBREDDIT_CONFIG.keys())}\n")
            
            f.write("USER CRITERIA:\n")
            f.write(USER_PROMPT)
            
            f.write("AI ANALYSIS:\n")
            f.write(analysis)
            
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
    Enhanced workflow:
    1. Fetch all posts directly (no LLM)
    2. Fetch all comments directly (no LLM)
    3. Save raw data to file
    4. Run AI analysis based on user criteria
    5. Save analysis to separate file
    """
    
    required_vars = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        return
    
    print("🤖 REDDIT DATA FETCHER & ANALYZER")
    print(f"⏰ Time Filter: {TIME_FILTER.value}")
    print(f"📊 Subreddits: {list(SUBREDDIT_CONFIG.keys())}")

    async with httpx.AsyncClient(timeout=120) as http_client:
        reddit_client = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="reddit-analyzer/2.0"
        )
        
        deps = AppDeps(reddit_client=reddit_client, http_client=http_client)
        
        try:
            # ========== STEP 1: FETCH ALL POSTS ==========
            print(f"\n📝 STEP 1: Fetching posts from {len(SUBREDDIT_CONFIG)} subreddits...\n")
            
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
            
            print(f"\n✅ STEP 1 COMPLETE: Found {len(all_links)} posts\n")
            
            # ========== STEP 2: FETCH COMMENTS ==========
            print(f"📝 STEP 2: Fetching comments for {len(all_links)} posts...\n")
            
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
                
                # Rate limiting
                if i < len(all_links):
                    await asyncio.sleep(1)
            
            print(f"\n✅ STEP 2 COMPLETE: Fetched comments for all posts\n")
            
            # ========== STEP 3: SAVE RAW DATA ==========
            print("📝 STEP 3: Saving raw data to file...\n")
            
            # Combine all data
            full_data = "\n\n".join(all_comments_text)
            
            # Save raw data to file
            raw_filename = save_data_to_file(full_data, all_links)
            if raw_filename:
                print(f"💾 Raw data saved to: {raw_filename}")
                print(f"📄 Contains: {len(all_links)} posts with comments")
            
            # ========== STEP 4: AI ANALYSIS ==========
            print("🧠 STEP 4: Running AI analysis...\n")
            print("⏳ This may take a few minutes depending on data size...")
            
            result = await agent.run(
                USER_PROMPT + f"\nAnalyze this Reddit data:\n{full_data}",
                deps=deps
            )
            
            # ========== STEP 5: SAVE ANALYSIS ==========
            print("📝 STEP 5: Saving AI analysis to file...\n")
            
            analysis_filename = save_analysis_to_file(result.output, all_links)
            if analysis_filename:
                print(f"🧠 AI analysis saved to: {analysis_filename}")
            
            # ========== DISPLAY RESULTS ==========
            print("\n" + "="*60)
            print("🧠 AI ANALYSIS RESULTS")
            print("="*60)
            print(result.output)
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await reddit_client.close()
    
    print(f"\n✅ COMPLETE! Generated files:")
    if 'raw_filename' in locals() and raw_filename:
        print(f"   📄 Raw data: {raw_filename}")
    if 'analysis_filename' in locals() and analysis_filename:
        print(f"   🧠 Analysis: {analysis_filename}")


if __name__ == "__main__":
    asyncio.run(main())