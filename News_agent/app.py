"""
Main Gradio application with Manual Analysis and Scheduler tabs.
"""
import gradio as gr
from datetime import datetime

from workflow import run_complete_workflow
from scheduler import scheduler, initialize_scheduler
from utils import parse_subreddit_config, format_subreddit_config
from config import (
    DEFAULT_SUBREDDIT_CONFIG,
    DEFAULT_TIME_FILTER,
    DEFAULT_TOP_COMMENTS,
    DEFAULT_REPLIES_PER_COMMENT,
    DEFAULT_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT,
    DEFAULT_SCHEDULE_HOUR,
    DEFAULT_SCHEDULE_MINUTE
)


# =============================================================================
# MANUAL ANALYSIS FUNCTIONS
# =============================================================================

async def run_manual_analysis(
    subreddit_config: str,
    time_filter: str,
    top_comments: int,
    replies_per_comment: int,
    model: str,
    system_prompt: str,
    user_prompt: str,
    send_to_telegram: bool
):
    """Run manual analysis from Gradio UI."""
    
    # Parse subreddit config
    subreddit_dict = parse_subreddit_config(subreddit_config)
    
    if not subreddit_dict:
        return "❌ Invalid subreddit configuration. Use format: SubredditName:PostLimit, SubredditName2:PostLimit", None, None, None
    
    # Run workflow
    analysis_file, raw_data_file = await run_complete_workflow(
        subreddit_config=subreddit_dict,
        time_filter=time_filter,
        top_comments=int(top_comments),
        replies_per_comment=int(replies_per_comment),
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        send_to_telegram=send_to_telegram
    )
    
    if analysis_file and analysis_file.endswith(".txt"):
        # Read file content
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Read raw data content
            raw_content = None
            if raw_data_file:
                with open(raw_data_file, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
            
            return (
                f"✅ Analysis complete!\n📄 Analysis: {analysis_file}\n📊 Raw Data: {raw_data_file}",
                content,
                analysis_file,
                raw_data_file
            )
        except Exception as e:
            return f"✅ Files saved\n❌ Error reading files: {str(e)}", None, None, None
    else:
        return f"❌ {analysis_file}", None, None, None


# =============================================================================
# SCHEDULER FUNCTIONS
# =============================================================================

def enable_schedule(
    hour: int,
    minute: int,
    timezone: str,
    subreddit_config: str,
    time_filter: str,
    top_comments: int,
    replies_per_comment: int,
    model: str,
    system_prompt: str,
    user_prompt: str
):
    """Enable/update schedule from Gradio UI."""
    
    config = {
        "subreddit_config": subreddit_config,
        "time_filter": time_filter,
        "top_comments": top_comments,
        "replies_per_comment": replies_per_comment,
        "model": model,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    }
    
    success = scheduler.save_config(
        enabled=True,
        hour=int(hour),
        minute=int(minute),
        timezone=timezone,
        config=config
    )
    
    if success:
        scheduler.restart()
        status = get_schedule_status()
        return f"✅ Schedule enabled: Daily at {int(hour):02d}:{int(minute):02d} {timezone}", status
    else:
        return "❌ Failed to save schedule configuration", "Error"


def disable_schedule():
    """Disable schedule from Gradio UI."""
    if scheduler.config_file.exists():
        config = scheduler.load_config()
        scheduler.save_config(
            enabled=False,
            hour=config.get('hour', 9),
            minute=config.get('minute', 0),
            timezone=config.get('timezone', 'Etc/UTC'),
            config=config.get('config', {})
        )
    
    scheduler.stop()
    status = get_schedule_status()
    return "🛑 Schedule disabled", status


def get_schedule_status():
    """Get schedule status for display."""
    status = scheduler.get_status()
    
    if status['enabled'] and status['running']:
        return f"""✅ **Scheduler Active**

📅 **Scheduled Time:** {status['scheduled_time']} {status['timezone']}
⏰ **Next Run:** {status['next_run']}
🕐 **Current Time:** {status['current_time']}
"""
    elif status['enabled']:
        return f"⚠️ Schedule enabled but not running. Click 'Enable Schedule' to start."
    else:
        return "🛑 Scheduler is disabled"


# =============================================================================
# GRADIO UI
# =============================================================================

def create_app():
    """Create Gradio application."""
    
    # Detect system timezone
    try:
        local_tz = str(datetime.now().astimezone().tzinfo)
    except:
        local_tz = "Etc/UTC"
    
    with gr.Blocks(
        title="Reddit AI Analyzer", 
        theme=gr.themes.Soft(),
        css = """
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }
        textarea, input, .output-text {
            font-feature-settings: normal !important;
            text-rendering: optimizeLegibility !important;
        }
    """
    ) as demo:
        
        gr.Markdown("# 🤖 Reddit AI Analyzer", elem_classes="emoji")
        gr.Markdown(
            "Analyze Reddit posts and comments using AI to extract insights and trends. "
            "Perfect for staying updated on AI news and discussions!",
            elem_classes="emoji"
        )
        
        with gr.Tabs():
            
            # ===== MANUAL ANALYSIS TAB =====
            with gr.Tab("📊 Manual Analysis"):
                gr.Markdown("## Run Analysis Now")
                gr.Markdown("Configure and run a one-time Reddit analysis")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📝 Analysis Configuration")
                        
                        manual_subreddit = gr.Textbox(
                            label="Subreddit Configuration",
                            value=format_subreddit_config(DEFAULT_SUBREDDIT_CONFIG),
                            placeholder="LocalLLaMA:10, artificial:5, MachineLearning:2",
                            info="Format: SubredditName:PostLimit, SubredditName2:PostLimit"
                        )
                        
                        manual_time_filter = gr.Dropdown(
                            label="Time Filter",
                            choices=["hour", "day", "week", "month", "year", "all"],
                            value=DEFAULT_TIME_FILTER.value,
                            info="Time period for top posts"
                        )
                        
                        with gr.Row():
                            manual_top_comments = gr.Number(
                                label="Top Comments",
                                value=DEFAULT_TOP_COMMENTS,
                                minimum=1,
                                maximum=10,
                                step=1,
                                info="Number of top comments per post (max 10)"
                            )
                            
                            manual_replies = gr.Number(
                                label="Replies per Comment",
                                value=DEFAULT_REPLIES_PER_COMMENT,
                                minimum=1,
                                maximum=5,
                                step=1,
                                info="Number of replies per comment (max 5)"
                            )
                        
                        manual_model = gr.Dropdown(
                            label="AI Model",
                            choices=["gemini-2.5-pro", "gemini-2.5-flash", "openai:gpt-4o", "openai:gpt-4o-mini", "openai:gpt-5"],
                            value=DEFAULT_MODEL,
                            info="AI model for analysis"
                        )
                    
                    with gr.Column():
                        gr.Markdown("### 🎯 Analysis Criteria")
                        
                        manual_user_prompt = gr.Textbox(
                            label="What to Look For",
                            value=DEFAULT_USER_PROMPT,
                            lines=6,
                            info="Tell the AI what insights you're looking for"
                        )
                        
                        manual_send_telegram = gr.Checkbox(
                            label="📱 Send results to Telegram",
                            value=False,
                            info="Send analysis file to your Telegram bot"
                        )
                
                gr.Markdown("### 🧠 System Prompt (Advanced)")
                manual_system_prompt = gr.Textbox(
                    label="System Instructions",
                    value=DEFAULT_SYSTEM_PROMPT,
                    lines=8,
                    info="Instructions for how the AI should analyze"
                )
                
                manual_run_btn = gr.Button("▶️ Run Analysis Now", variant="primary", size="lg")
                manual_result = gr.Textbox(label="Result", interactive=False, lines=3)
                
                # Add content display with copy and download
                with gr.Row():
                    manual_content = gr.Textbox(
                        label="Analysis Output",
                        interactive=False,
                        lines=20,
                        max_lines=30,
                        show_copy_button=True,
                        visible=False
                    )
                
                with gr.Row():
                    with gr.Column():
                        manual_download = gr.File(
                            label="📄 Download Analysis File",
                            visible=False
                        )
                    with gr.Column():
                        manual_raw_download = gr.File(
                            label="📊 Download Raw Reddit Data",
                            visible=False
                        )
                
                manual_run_btn.click(
                    fn=run_manual_analysis,
                    inputs=[
                        manual_subreddit,
                        manual_time_filter,
                        manual_top_comments,
                        manual_replies,
                        manual_model,
                        manual_system_prompt,
                        manual_user_prompt,
                        manual_send_telegram
                    ],
                    outputs=[manual_result, manual_content, manual_download, manual_raw_download]
                ).then(
                    # Show content and downloads if they exist
                    fn=lambda content, file, raw: (
                        gr.update(visible=content is not None),
                        gr.update(visible=file is not None),
                        gr.update(visible=raw is not None)
                    ),
                    inputs=[manual_content, manual_download, manual_raw_download],
                    outputs=[manual_content, manual_download, manual_raw_download]
                )
            
            # ===== SCHEDULER TAB =====
            with gr.Tab("⏰ Scheduler"):
                gr.Markdown("## Schedule Automatic Daily Analysis")
                gr.Markdown(
                    "Set up automatic daily analysis that runs at a specified time "
                    "and sends results to your Telegram bot."
                )
                
                gr.Markdown(f"**Current System Timezone:** {local_tz}")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### ⏰ Schedule Configuration")
                        
                        schedule_hour = gr.Number(
                            label="Hour (24-hour format)",
                            value=DEFAULT_SCHEDULE_HOUR,
                            minimum=0,
                            maximum=23,
                            step=1,
                            info="Hour of day to run (0-23)"
                        )
                        
                        schedule_minute = gr.Number(
                            label="Minute",
                            value=DEFAULT_SCHEDULE_MINUTE,
                            minimum=0,
                            maximum=59,
                            step=1,
                            info="Minute of hour to run (0-59)"
                        )
                        
                        schedule_timezone = gr.Textbox(
                            label="Timezone",
                            value=local_tz,
                            placeholder="e.g., America/New_York, Europe/London, Etc/UTC",
                            info="Timezone for schedule"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 Schedule Status")
                        
                        status_display = gr.Markdown(value=get_schedule_status())
                        
                        refresh_status_btn = gr.Button("🔄 Refresh Status", size="sm")
                
                gr.Markdown("### 📝 Analysis Configuration")
                gr.Markdown("Configure what analysis to run automatically")
                
                schedule_subreddit = gr.Textbox(
                    label="Subreddit Configuration",
                    value=format_subreddit_config(DEFAULT_SUBREDDIT_CONFIG),
                    placeholder="LocalLLaMA:10, artificial:5"
                )
                
                schedule_time_filter = gr.Dropdown(
                    label="Time Filter",
                    choices=["hour", "day", "week", "month", "year", "all"],
                    value=DEFAULT_TIME_FILTER.value
                )
                
                with gr.Row():
                    schedule_top_comments = gr.Number(
                        label="Top Comments",
                        value=DEFAULT_TOP_COMMENTS,
                        minimum=1,
                        maximum=10
                    )
                    schedule_replies = gr.Number(
                        label="Replies per Comment",
                        value=DEFAULT_REPLIES_PER_COMMENT,
                        minimum=1,
                        maximum=5
                    )
                
                schedule_model = gr.Dropdown(
                    label="AI Model",
                    choices=["gemini-2.5-pro", "openai:gpt-4o", "openai:gpt-4o-mini"],
                    value=DEFAULT_MODEL
                )
                
                schedule_system_prompt = gr.Textbox(
                    label="System Prompt",
                    value=DEFAULT_SYSTEM_PROMPT,
                    lines=6
                )
                
                schedule_user_prompt = gr.Textbox(
                    label="User Criteria",
                    value=DEFAULT_USER_PROMPT,
                    lines=4
                )
                
                gr.Markdown("---")
                
                with gr.Row():
                    enable_schedule_btn = gr.Button("✅ Enable Schedule", variant="primary", size="lg")
                    disable_schedule_btn = gr.Button("🛑 Disable Schedule", variant="stop", size="lg")
                
                schedule_result = gr.Textbox(label="Result", interactive=False)
                
                # Event handlers
                enable_schedule_btn.click(
                    fn=enable_schedule,
                    inputs=[
                        schedule_hour, schedule_minute, schedule_timezone,
                        schedule_subreddit, schedule_time_filter,
                        schedule_top_comments, schedule_replies,
                        schedule_model, schedule_system_prompt, schedule_user_prompt
                    ],
                    outputs=[schedule_result, status_display]
                )
                
                disable_schedule_btn.click(
                    fn=disable_schedule,
                    outputs=[schedule_result, status_display]
                )
                
                refresh_status_btn.click(
                    fn=get_schedule_status,
                    outputs=status_display
                )
                
                gr.Markdown("""
                ### 📋 How It Works
                
                1. **Configure Time**: Set hour and minute for daily analysis
                2. **Configure Analysis**: Set subreddits and AI parameters
                3. **Enable**: Click "Enable Schedule" to start
                4. **Automatic**: Analysis runs daily at specified time
                5. **Telegram**: Results are automatically sent to your Telegram bot
                
                ### 📝 Notes:
                
                - Schedule persists across Docker restarts
                - Container must be running for scheduled jobs
                - Results are ALWAYS sent to Telegram for scheduled runs
                - Check status to see next scheduled run time
                """)
    
    return demo


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Initialize scheduler before launching app
    initialize_scheduler()
    
    # Create and launch app
    demo = create_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )