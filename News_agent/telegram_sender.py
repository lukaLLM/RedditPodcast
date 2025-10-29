"""
Telegram bot message and file sending.
"""
import os
from telegram import Bot


async def send_telegram_message(message: str, parse_mode: str = "Markdown") -> bool:
    """
    Send a text message to Telegram.
    
    Args:
        message: Message text to send
        parse_mode: "Markdown" or None
        
    Returns:
        bool: Success status
    """
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            print("❌ Telegram credentials not configured")
            return False
        
        bot = Bot(token=bot_token)
        
        # Escape special characters for Markdown
        if parse_mode == "Markdown":
            safe_message = message.replace("_", "\\_").replace("[", "\\[").replace("]", "\\]")
        else:
            safe_message = message
        
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
    """
    Send a document to Telegram.
    
    Args:
        file_path: Path to file to send
        caption: Optional caption text
        
    Returns:
        bool: Success status
    """
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


async def send_analysis_results(
    analysis_file: str,
    subreddit_config: dict,
    time_filter: str,
    num_posts: int
) -> bool:
    """
    Send analysis results to Telegram (message + file).
    
    Args:
        analysis_file: Path to analysis text file
        subreddit_config: Dict of analyzed subreddits
        time_filter: Time filter used
        num_posts: Number of posts analyzed
        
    Returns:
        bool: Success status
    """
    # Prepare message
    message = f"🤖 *Reddit AI Analysis Complete*\n\n"
    message += f"📊 *Analyzed:* {num_posts} posts\n"
    message += f"📁 *Subreddits:* {', '.join(subreddit_config.keys())}\n"
    message += f"⏰ *Time Filter:* {time_filter}\n\n"
    message += f"📄 *Full analysis file attached below*"
    
    # Send message
    msg_success = await send_telegram_message(message)
    
    # Send file
    file_success = await send_telegram_document(
        analysis_file,
        caption="📄 Full AI Analysis Report"
    )
    
    return msg_success and file_success


async def send_error_notification(error_message: str) -> bool:
    """
    Send error notification to Telegram.
    
    Args:
        error_message: Error message to send
        
    Returns:
        bool: Success status
    """
    message = f"❌ *Error in Reddit Analysis*\n\n```{error_message}```"
    return await send_telegram_message(message)