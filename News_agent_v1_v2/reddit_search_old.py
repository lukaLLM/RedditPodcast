# =============================================================================
# REDDIT AI ANALYZER WITH COMMENTS
# Fetches top posts from AI subreddits and analyzes with GPT-5
# =============================================================================

import asyncio
import os
import re
import time  # Add this import
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

from asyncpraw.models.reddit.subreddit import Subreddit
import httpx
import asyncpraw
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
import logfire

# =============================================================================
# CONFIGURATION & SETUP
# =============================================================================

load_dotenv()

# Configure Logfire for debugging
logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
logfire.instrument_pydantic_ai()

# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class AppDeps:
    """
    Dependencies container for PydanticAI agent.
    
    Attributes:
        reddit_client: Async Reddit API client
        http_client: HTTP client for potential web requests
    """
    reddit_client: asyncpraw.Reddit
    http_client: httpx.AsyncClient


# =============================================================================
# REDDIT API FUNCTIONS (Tools for AI Agent)
# =============================================================================

async def get_top_posts_today(
    ctx: RunContext[AppDeps], 
    subreddit: str,
    limit: int = 10
) -> str:
    """
    Fetches TODAY's top posts from a specific subreddit.
    
    Args:
        ctx: PydanticAI context containing dependencies
        subreddit: Subreddit name WITHOUT "r/" (e.g., "LocalLLaMA")
        limit: Max posts to fetch (capped at 10 for performance)
    
    Returns:
        Formatted string with post details OR error message
    """
    try:
        # Cap limit to prevent overwhelming the API
        limit = min(limit, 10)
        print(f"\n🔍 Getting TOP posts from r/{subreddit} (today)...")

        # Get subreddit object from Reddit API
        subreddit_obj: Subreddit = await ctx.deps.reddit_client.subreddit(subreddit)
        
        results = []
        post_count = 0

        # Fetch posts from Reddit
        # time_filter="day" = only today's posts
        async for post in subreddit_obj.top(time_filter="day", limit=limit):
            post_count += 1
            
            # Extract content preview (first 300 chars)
            content_preview = ""
            if post.selftext:  # selftext = post body text
                content_preview = post.selftext[:300].replace("\n", " ")
                if len(post.selftext) > 300:
                    content_preview += "..."
            
            # Build post dictionary
            results.append({
                "title": post.title,
                "score": post.score,  # Upvotes - downvotes
                "comments": post.num_comments,
                "subreddit": post.subreddit.display_name,
                "url": f"https://reddit.com{post.permalink}",
                "content_preview": content_preview
            })

            # Progress feedback
            print(f"   ✓ {post.title[:70]}... ({post.score} ⬆️, {post.num_comments} 💬)")
        
        print(f"✅ Found {post_count} posts from r/{subreddit}\n")

        # Format results for GPT (human-readable format)
        formatted = f"=== TOP POSTS from r/{subreddit} (today) ===\n\n"
        
        for i, post in enumerate(results, 1):
            formatted += f"{i}. **{post['title']}**\n"
            formatted += f"   📍 r/{post['subreddit']}"
            formatted += f"   👍 {post['score']} upvotes | 💬 {post['comments']} comments\n"
            if post['content_preview']:
                formatted += f"   📝 {post['content_preview']}\n"
            formatted += f"   🔗 {post['url']}\n\n"
        
        return formatted.strip()
        
    except Exception as e:
        # Return error as string so GPT knows what went wrong
        return f"❌ Error getting posts from r/{subreddit}: {str(e)}"


async def get_post_with_nested_comments(
    ctx: RunContext[AppDeps],
    post_url: str,
    top_comments_limit: int = 5,
    replies_per_comment: int = 5
) -> str:
    """
    Fetches a post with top comments AND their top replies.
    
    Args:
        ctx: PydanticAI context
        post_url: Full Reddit URL
        top_comments_limit: Number of top-level comments to fetch (max 10)
        replies_per_comment: Number of top replies per comment to fetch (max 5)
    
    Returns:
        Formatted string with post + comments + nested replies
    """
    try:
        top_comments_limit = min(top_comments_limit, 10)
        replies_per_comment = min(replies_per_comment, 5)
        
        print(f"\n💬 Fetching post with nested comments...")
        print(f"   📊 Top comments: {top_comments_limit}")
        print(f"   📊 Replies per comment: {replies_per_comment}")
        
        submission = await ctx.deps.reddit_client.submission(url=post_url)
        await submission.load()
        
        # CHANGED: limit=1 allows expanding one level of nested comments
        # Higher numbers = more nested levels, but slower
        await submission.comments.replace_more(limit=1)
        
        # Get top-level comments sorted by score
        top_level_comments = sorted(
            submission.comments, 
            key=lambda c: c.score, 
            reverse=True
        )[:top_comments_limit]
        
        comments_data = []
        
        for comment in top_level_comments:
            # Truncate long comments
            comment_text = comment.body[:500]
            if len(comment.body) > 500:
                comment_text += "..."
            
            # Get top replies to this comment
            replies_data = []
            if hasattr(comment, 'replies') and comment.replies:
                # Sort replies by score
                top_replies = sorted(
                    comment.replies,
                    key=lambda r: r.score if hasattr(r, 'score') else 0,
                    reverse=True
                )[:replies_per_comment]
                
                for reply in top_replies:
                    if hasattr(reply, 'body'):  # Make sure it's a comment, not MoreComments
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
            
            print(f"   ✓ Comment ({comment.score} ⬆️) with {len(replies_data)} replies")
        
        print(f"✅ Fetched post with {len(comments_data)} comments\n")
        
        # Format output
        formatted = f"=== POST DETAILS ===\n\n"
        formatted += f"**{submission.title}**\n"
        formatted += f"📍 r/{submission.subreddit.display_name}\n"
        formatted += f"👍 {submission.score} upvotes | 💬 {submission.num_comments} comments\n"
        formatted += f"🔗 {post_url}\n\n"
        
        if submission.selftext:
            content = submission.selftext[:1000].replace("\n", " ")
            if len(submission.selftext) > 1000:
                content += "..."
            formatted += f"**Post Content:**\n{content}\n\n"
        
        formatted += f"=== TOP {len(comments_data)} COMMENTS WITH REPLIES ===\n\n"
        
        for i, comment in enumerate(comments_data, 1):
            formatted += f"{i}. ({comment['score']} ⬆️)\n"
            formatted += f"   {comment['text']}\n"
            
            # Add nested replies
            if comment['replies']:
                formatted += f"\n   💬 Top {len(comment['replies'])} replies:\n"
                for j, reply in enumerate(comment['replies'], 1):
                    formatted += f"   {i}.{j}. ({reply['score']} ⬆️) {reply['text']}\n"
            
            formatted += "\n"
        
        return formatted.strip()
        
    except Exception as e:
        return f"❌ Error fetching post comments: {str(e)}"



# AI AGENT SETUP

# Create AI agent with Reddit tools
agent = Agent(
    "google-gla:gemini-2.5-pro",  # Model to use # google-gla:gemini-2.5-flash openai:gpt-5
    deps_type=AppDeps,  # Type of dependencies
    tools=[get_top_posts_today, get_post_with_nested_comments],  # Available functions
    system_prompt=(
        """
        You are a Reddit research assistant. Follow the user's instructions carefully.
        Use get_top_posts_today to fetch posts and get_post_with_nested_comments to fetch comments.
        Always include the full Reddit URLs in your response.
        """
    )
)

# OUTPUT FORMATTING HELPERS

def extract_reddit_links(text: str) -> List[str]:
    """
    Extracts all Reddit URLs from text.
    
    Args:
        text: Text to search for URLs
        
    Returns:
        List of Reddit URLs found
    """
    # Regex: Match reddit.com URLs until whitespace or closing bracket
    return re.findall(r'https://(?:www\.)?reddit\.com[^\s\)]+', text)


def save_summary_to_file(summary: str, links: List[str]) -> str:
    """
    Saves analysis summary and links to timestamped file.
    
    Args:
        summary: GPT analysis text
        links: List of Reddit URLs
        
    Returns:
        Filename where summary was saved
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename: str = f"reddit_summary_{timestamp}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Header
            f.write("REDDIT AI COMMUNITY DAILY SUMMARY (with Comments)\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            # Main summary
            f.write(summary)
            
            # Append all links at the end
            if links:
                f.write(f"🔗 ALL REDDIT LINKS ({len(links)} posts)\n")
                for i, link in enumerate(links, 1):
                    f.write(f"{i}. {link}\n")
        
        return filename
        
    except IOError as e:
        print(f"❌ Failed to save file: {e}")
        return None

async def main():
    """
    Main execution function.
    
    Process:
    1. Check environment variables
    2. Initialize Reddit and HTTP clients
    3. Create dependencies container
    4. STEP 1: Get all posts from subreddits
    5. STEP 2: Get comments for each post and analyze
    6. Extract results and save to file
    """
    
    # Check required environment variables
    required_vars = ["GOOGLE_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        return
    
    print("🤖 REDDIT TOP POSTS ANALYZER (with Comments)")
    
    # Initialize clients with context manager (auto-closes on exit)
    async with httpx.AsyncClient(timeout=120) as http_client:
        reddit_client = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="reddit-top-analyzer/1.0"
        )
        
        try: 
            # Create dependencies container
            deps = AppDeps(
                reddit_client=reddit_client,
                http_client=http_client
            )
            
            # ========== STEP 1: GET ALL POSTS ==========
            
            posts_query = """
            Get top posts from TODAY from these subreddits:
            - r/LocalLLaMA (10 posts)
            - r/artificial (5 posts)
            - r/MachineLearning (2 posts)
            - r/OpenAI (2 post)
            - r/AI_Agents (2 posts)
            - r/ArtificialInteligence (5 posts)
   
            Return all post titles and their Reddit URLs.
            """
                        
            print(f"\n📝 STEP 1: Fetching posts from subreddits...\n")
            
            # Run agent to get posts
            posts_result = await agent.run(posts_query, deps=deps)
            
            # Extract all Reddit links from GPT's response
            links = extract_reddit_links(posts_result.output)
            
            if not links:
                print("❌ No posts found!")
                return
            
            print(f"\n✅ Found {len(links)} posts\n")
            
            # ========== RATE LIMIT DELAY ==========
            await asyncio.sleep(50)  # Wait 50 seconds between API calls
            
            # ========== STEP 2: GET COMMENTS FOR EACH POST ==========
            
            print(f"📝 STEP 2: Fetching comments for {len(links)} posts...\n")
            
            comments_query = f"""
            Fetch the top 10 comments with replies for EACH of these {len(links)} posts:
            
            {chr(10).join(links)}

            Then analyze all posts and their comments to provide:
            1. Key themes and trends across all discussions
            2. Most interesting or impactful discussions
            3. Notable insights from the community
            4. A brief summary of each post's main discussion points
            
            Include all Reddit URLs in your final summary.
            """
            
            # Run agent to get comments and analyze
            final_result = await agent.run(comments_query, deps=deps)
            
            # PROCESS RESULTS
            
            # Extract all Reddit links from GPT's final response
            final_links = extract_reddit_links(final_result.output)
            
            # Print GPT analysis
            print("\n" + "="*80)
            print("📊 GEMINI ANALYSIS & SUMMARY")
            print("="*80 + "\n")
            print(final_result.output)
            
            # Save to file
            filename = save_summary_to_file(final_result.output, final_links)
            if filename:
                print(f"\n💾 Summary saved to: {filename}")
                print(f"📄 File includes: Analysis + All {len(final_links)} Reddit links at the end")
            
        finally:
            # Clean up Reddit client
            await reddit_client.close()
    
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())