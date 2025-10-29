"""
Reddit API interaction functions.
"""
import asyncio
from typing import List, Tuple
import asyncpraw
from asyncpraw.models.reddit.subreddit import Subreddit

async def fetch_top_posts(
    reddit_client: asyncpraw.Reddit,
    subreddit: str,
    limit: int = 10,
    time_filter: str = "day"
) -> Tuple[str, List[str]]:
    """
    Fetch top posts from a subreddit.
    
    Args:
        reddit_client: Async Reddit client
        subreddit: Subreddit name
        limit: Number of posts to fetch (max 10)
        time_filter: Time period (hour, day, week, month, year, all)
        
    Returns:
        tuple: (formatted_text, list_of_urls)
    """
    try:
        limit = min(limit, 10)  # Reddit API limit
        print(f"\n🔍 Fetching top {limit} posts from r/{subreddit} ({time_filter})...")

        subreddit_obj: Subreddit = await reddit_client.subreddit(subreddit)
        
        results = []
        urls = []
        post_count = 0

        async for post in subreddit_obj.top(time_filter=time_filter, limit=limit):
            post_count += 1
            
            # Get content preview
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

        # Format results
        formatted = f"=== TOP POSTS from r/{subreddit} ({time_filter}) ===\n\n"
        
        for i, post in enumerate(results, 1):
            formatted += f"{i}. {post['title']}\n"
            formatted += f"   📍 r/{post['subreddit']} | "
            formatted += f"👍 {post['score']} upvotes | 💬 {post['comments']} comments\n"
            if post['content_preview']:
                formatted += f"   📝 {post['content_preview']}\n"
            formatted += f"   🔗 {post['url']}\n\n"
        
        return formatted.strip(), urls
        
    except Exception as e:
        error_msg = f"❌ Error fetching posts from r/{subreddit}: {str(e)}"
        print(error_msg)
        return error_msg, []


async def fetch_post_comments(
    reddit_client: asyncpraw.Reddit,
    post_url: str,
    top_comments_limit: int = 10,
    replies_per_comment: int = 5
) -> str:
    """
    Fetch a post with its top comments and replies.
    
    Args:
        reddit_client: Async Reddit client
        post_url: Full URL to Reddit post
        top_comments_limit: Number of top-level comments (max 10)
        replies_per_comment: Number of replies per comment (max 5)
        
    Returns:
        str: Formatted post with comments
    """
    try:
        top_comments_limit = min(top_comments_limit, 10)
        replies_per_comment = min(replies_per_comment, 5)
        
        # Fetch submission
        submission = await reddit_client.submission(url=post_url)
        await submission.load()
        await submission.comments.replace_more(limit=1)
        
        # Get top comments sorted by score
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
            formatted += f"\nPost Content:\n{content}\n\n"
        
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
        error_msg = f"❌ Error fetching comments from {post_url}: {str(e)}"
        print(error_msg)
        return error_msg


async def fetch_all_reddit_data(
    reddit_client: asyncpraw.Reddit,
    subreddit_config: dict,
    time_filter: str = "day",
    top_comments: int = 10,
    replies_per_comment: int = 5
) -> Tuple[str, str]:
    """
    Fetch all posts and comments from multiple subreddits.
    
    Args:
        reddit_client: Async Reddit client
        subreddit_config: Dict of {subreddit_name: post_limit}
        time_filter: Time period filter
        top_comments: Number of top comments per post
        replies_per_comment: Number of replies per comment
        
    Returns:
        tuple: (full_formatted_data, raw_reddit_data)
    """
    all_posts_text = []
    all_links = []
    
    # Fetch posts from all subreddits
    print(f"📝 STEP 1: Fetching posts from {len(subreddit_config)} subreddits...\n")
    
    for subreddit_name, limit in subreddit_config.items():
        posts_text, urls = await fetch_top_posts(
            reddit_client,
            subreddit=subreddit_name,
            limit=limit,
            time_filter=time_filter
        )
        all_posts_text.append(posts_text)
        all_links.extend(urls)
    
    if not all_links:
        raise ValueError("No posts found from any subreddit")
    
    print(f"\n✅ Found {len(all_links)} posts total\n")
    
    # Fetch comments for all posts
    print(f"📝 STEP 2: Fetching comments from {len(all_links)} posts...\n")
    
    all_comments_text = []
    raw_posts_data = []
    
    for i, link in enumerate(all_links, 1):
        print(f"[{i}/{len(all_links)}] {link}")
        comments_text = await fetch_post_comments(
            reddit_client,
            post_url=link,
            top_comments_limit=top_comments,
            replies_per_comment=replies_per_comment
        )
        all_comments_text.append(comments_text)
        
        # Create clean raw data entry
        raw_post_entry = f"LINK: {link}\n\n{comments_text}\n\n{'='*80}\n\n"
        raw_posts_data.append(raw_post_entry)
        
        # Rate limiting
        if i < len(all_links):
            await asyncio.sleep(1)
    
    full_data = "\n\n".join(all_comments_text)
    
    # Create clean raw data export with just links and comments
    raw_data = "REDDIT RAW DATA - POSTS AND COMMENTS\n"
    raw_data += "="*80 + "\n\n"
    raw_data += "".join(raw_posts_data)
    
    print(f"\n✅ Comments fetched\n")
    
    return full_data, raw_data