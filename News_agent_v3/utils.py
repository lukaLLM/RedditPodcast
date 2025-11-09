"""
Utility helper functions.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from config import OUTPUTS_DIR, SCHEDULER_DIR

def ensure_outputs_dir():
    """Ensure outputs directory exists."""
    # Just create if missing - don't try to chmod volume mounts
    Path(OUTPUTS_DIR).mkdir(exist_ok=True, parents=True)
    Path(SCHEDULER_DIR).mkdir(exist_ok=True, parents=True)  # 

def save_analysis_to_file(
    analysis: str,
    subreddit_config: Dict[str, int],
    time_filter: str,
    model: str,
    raw_reddit_data: str = None,
    run_folder: Optional[Path] = None  # 
) -> tuple[str, str, Path]:  # 
    """
    Save AI analysis to timestamped file in organized folder structure.
    
    Returns:
        tuple: (path_to_analysis_file, path_to_raw_data_file, run_folder)
    """
    ensure_outputs_dir()
    
    # Use provided folder or create new one
    if run_folder is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_folder = Path(OUTPUTS_DIR) / f"run_{timestamp}"
        run_folder.mkdir(exist_ok=True, parents=True)
    
    # File paths within the run folder
    analysis_filename = run_folder / "analysis.txt"
    raw_data_filename = run_folder / "raw_data.txt"
    
    try:
        # Count posts from raw data
        num_posts = raw_reddit_data.count("LINK: https://reddit.com") if raw_reddit_data else 0
        
        # Save analysis file
        with open(analysis_filename, "w", encoding="utf-8") as f:
            f.write("🧠 AI ANALYSIS REPORT\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Time Filter: {time_filter}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Posts Analyzed: {num_posts}\n")
            f.write(f"Subreddits: {', '.join(subreddit_config.keys())}\n\n")
            f.write("---\n\n")
            f.write(analysis)
        
        # Save raw Reddit data
        if raw_reddit_data:
            with open(raw_data_filename, "w", encoding="utf-8") as f:
                f.write(raw_reddit_data)
        
        print(f"💾 Analysis saved: {analysis_filename}")
        print(f"💾 Raw data saved: {raw_data_filename}")
        
        return str(analysis_filename), str(raw_data_filename), run_folder  # ✅ Return folder
        
    except IOError as e:
        print(f"❌ Failed to save files: {e}")
        return None, None, None


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


def save_llm_input(
    reddit_data: str,
    email_data: Optional[str],
    system_prompt: str,
    user_prompt: str,
    model: str,
    combined_content: str,
    run_folder: Path  # ✅ Now required, not optional
) -> str:
    """Save the exact input that will be sent to the LLM."""
    
    filename = run_folder / "llm_input.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("LLM INPUT - EXACT PAYLOAD FOR ANALYSIS\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: {model}\n")
        f.write(f"Reddit Data Length: {len(reddit_data):,} characters\n")
        f.write(f"Email Data Length: {len(email_data) if email_data else 0:,} characters\n")
        f.write(f"Combined Length: {len(combined_content):,} characters\n")
        f.write(f"Has Email Data: {'Yes' if email_data else 'No'}\n\n")
        f.write("---\n\n")
        
        f.write("SYSTEM PROMPT:\n\n")
        f.write(system_prompt)
        f.write("\n\n---\n\n")
        
        f.write("USER PROMPT:\n\n")
        f.write(user_prompt)
        f.write("\n\n---\n\n")
        
        f.write("REDDIT DATA:\n\n")
        f.write(reddit_data)
        f.write("\n\n")
        
        if email_data:
            f.write("---\n\nEMAIL DATA:\n\n")
            f.write(email_data)
            f.write("\n\n")
        
        f.write("---\n\nFINAL COMBINED CONTENT:\n\n")
        f.write(combined_content)
    
    print(f"💾 Saved LLM input to: {filename}")
    return str(filename)


def save_email_data(emails: List[Dict[str, str]], run_folder: Path) -> str:
    """
    Save raw email data to JSON file.
    
    Args:
        emails: List of email dictionaries
        run_folder: Folder to save to (required)
    
    Returns:
        Path to saved file
    """
    import json
    
    filename = run_folder / "emails.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved email data to: {filename}")
    return str(filename)