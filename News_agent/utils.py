"""
Utility helper functions.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from config import OUTPUTS_DIR, DATA_DIR

def ensure_outputs_dir():
    """Ensure outputs directory exists."""
    # Just create if missing - don't try to chmod volume mounts
    Path(OUTPUTS_DIR).mkdir(exist_ok=True, parents=True)
    Path(DATA_DIR).mkdir(exist_ok=True, parents=True)

def save_analysis_to_file(
    analysis: str,
    subreddit_config: Dict[str, int],
    time_filter: str,
    model: str,
    raw_reddit_data: str = None
) -> tuple[str, str]:
    """
    Save AI analysis to timestamped file.
    
    Returns:
        tuple: (path_to_analysis_file, path_to_raw_data_file)
    """
    ensure_outputs_dir()
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    analysis_filename = f"{OUTPUTS_DIR}/reddit_analysis_{timestamp}.txt"
    raw_data_filename = f"{OUTPUTS_DIR}/reddit_raw_data_{timestamp}.txt"
    
    try:
        # Count posts from raw data
        num_posts = raw_reddit_data.count("LINK: https://reddit.com") if raw_reddit_data else 0
        
        # Save analysis file
        with open(analysis_filename, "w", encoding="utf-8") as f:
            f.write("🧠 AI ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Time Filter: {time_filter}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Posts Analyzed: {num_posts}\n")
            f.write(f"Subreddits: {', '.join(subreddit_config.keys())}\n\n")
            f.write("AI ANALYSIS\n\n")
            f.write(analysis)
        
        # Save raw Reddit data
        if raw_reddit_data:
            with open(raw_data_filename, "w", encoding="utf-8") as f:
                f.write(raw_reddit_data)
        
        print(f"💾 Analysis saved: {analysis_filename}")
        print(f"💾 Raw data saved: {raw_data_filename}")
        
        return analysis_filename, raw_data_filename
        
    except IOError as e:
        print(f"❌ Failed to save files: {e}")
        return None, None


def parse_subreddit_config(config_string: str) -> Dict[str, int]:
    """
    Parse subreddit configuration string.
    
    Format: "SubredditName:PostLimit, SubredditName2:PostLimit"
    Example: "LocalLLaMA:10, artificial:5"
    
    Returns:
        Dict[str, int]: Dictionary of subreddit names to post limits
    """
    subreddit_dict = {}
    
    for pair in config_string.split(','):
        pair = pair.strip()
        if ':' in pair:
            name, limit = pair.split(':', 1)
            try:
                subreddit_dict[name.strip()] = int(limit.strip())
            except ValueError:
                print(f"⚠️ Invalid limit for {name}: {limit}")
    
    return subreddit_dict


def format_subreddit_config(config_dict: Dict[str, int]) -> str:
    """
    Format subreddit dictionary to string.
    
    Returns:
        str: Formatted string like "LocalLLaMA:10, artificial:5"
    """
    return ", ".join(f"{name}:{limit}" for name, limit in config_dict.items())


def get_env_variable(name: str, required: bool = True) -> str:
    """
    Get environment variable with validation.
    
    Args:
        name: Environment variable name
        required: If True, raises error if not found
        
    Returns:
        str: Environment variable value or None
    """
    value = os.getenv(name)
    
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    
    return value


def validate_environment():
    """
    Validate all required environment variables are set.
    
    Returns:
        tuple: (bool, list) - (is_valid, missing_vars)
    """
    required_vars = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    return len(missing) == 0, missing