"""
Main Gradio application with unified interface for manual and scheduled analysis.
"""
import gradio as gr
from datetime import datetime

from workflow import run_complete_workflow
from scheduler import scheduler, initialize_scheduler
from utils import parse_subreddit_config, format_subreddit_config
from tts_service import TTSInference
from config import (
    DEFAULT_SUBREDDIT_CONFIG,
    DEFAULT_TIME_FILTER,
    DEFAULT_TOP_COMMENTS,
    DEFAULT_REPLIES_PER_COMMENT,
    DEFAULT_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT,
    DEFAULT_SCHEDULE_HOUR,
    DEFAULT_SCHEDULE_MINUTE,
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
    DEFAULT_ALLOWED_SENDERS,
    DEFAULT_EMAIL_HOURS_BACK,
    DEFAULT_MAX_EMAILS,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_TOP_K,
    DEFAULT_THINKING_BUDGET,  # ✅ Add
    MODEL_MAX_TOKENS
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
    send_to_telegram: bool,
    generate_tts: bool,
    tts_model: str,
    voice_name: str,
    tone_instructions: str,
    fetch_emails: bool,
    email_address: str,
    email_password: str,
    allowed_senders: str,
    email_hours_back: int,
    max_emails: int,
    max_output_tokens: int,
    temperature: float,
    top_p: float,
    top_k: int,
    thinking_budget: int  # ✅ Add
):
    """Run manual analysis from Gradio UI."""
    
    # Parse subreddit config string to dict
    subreddit_dict = parse_subreddit_config(subreddit_config)
    
    if not subreddit_dict:
        return "❌ Invalid subreddit configuration. Use format: SubredditName:PostLimit", None, None, None, None, None, None
    
    # Parse allowed senders
    sender_list = [s.strip() for s in allowed_senders.split(",") if s.strip()] if fetch_emails else None
    
    # Run workflow
    analysis_file, raw_data_file, audio_file, email_file, llm_input_file = await run_complete_workflow(
        subreddit_config=subreddit_dict,
        time_filter=time_filter,
        top_comments=int(top_comments),
        replies_per_comment=int(replies_per_comment),
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        send_to_telegram=send_to_telegram,
        generate_tts=generate_tts,
        tts_model=tts_model if generate_tts else None,
        voice_name=voice_name if generate_tts else None,
        tone_instructions=tone_instructions if generate_tts else None,
        fetch_emails=fetch_emails,
        email_address=email_address if fetch_emails else None,
        email_password=email_password if fetch_emails else None,
        allowed_senders=sender_list,
        email_hours_back=int(email_hours_back),
        max_emails=int(max_emails),
        max_output_tokens=int(max_output_tokens),
        temperature=float(temperature),
        top_p=float(top_p),
        top_k=int(top_k),
        thinking_budget=int(thinking_budget)  # ✅ Add
    )
    
    if analysis_file and analysis_file.endswith(".txt"):
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result_msg = f"✅ Analysis complete!\n📄 Analysis: {analysis_file}\n📊 Raw Data: {raw_data_file}"
            if audio_file:
                result_msg += f"\n🎙️ Audio: {audio_file}"
            if email_file:
                result_msg += f"\n📧 Emails: {email_file}"
            if llm_input_file:
                result_msg += f"\n🧠 LLM Input: {llm_input_file}"
            
            return (
                result_msg,
                content,
                analysis_file,
                raw_data_file,
                audio_file,
                email_file,
                llm_input_file
            )
        except Exception as e:
            return f"✅ Files saved\n❌ Error reading files: {str(e)}", None, None, None, None, None, None
    else:
        return f"❌ {analysis_file}", None, None, None, None, None, None


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
    user_prompt: str,
    generate_tts: bool,
    tts_model: str,
    voice_name: str,
    tone_instructions: str,
    fetch_emails: bool,
    email_address: str,
    email_password: str,
    allowed_senders: str,
    email_hours_back: int,
    max_emails: int,
    max_output_tokens: int,
    temperature: float,
    top_p: float,
    top_k: int,
    thinking_budget: int  # ✅ Add
):
    """Enable/update schedule using current form values."""
    
    config = {
        "subreddit_config": subreddit_config,
        "time_filter": time_filter,
        "top_comments": top_comments,
        "replies_per_comment": replies_per_comment,
        "model": model,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "generate_tts": generate_tts,
        "tts_model": tts_model if generate_tts else None,
        "voice_name": voice_name if generate_tts else None,
        "tone_instructions": tone_instructions if generate_tts else None,
        "fetch_emails": fetch_emails,
        "email_address": email_address if fetch_emails else None,
        "email_password": email_password if fetch_emails else None,
        "allowed_senders": allowed_senders,
        "email_hours_back": email_hours_back,
        "max_emails": max_emails,
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "thinking_budget": thinking_budget  # ✅ Add
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
        return f"✅ Schedule enabled: Daily at {int(hour):02d}:{int(minute):02d} {timezone}\n{status}"
    else:
        return "❌ Failed to save schedule configuration"


def disable_schedule():
    """Disable schedule."""
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
    return "🛑 Schedule disabled"


def get_schedule_status():
    """Get schedule status for display."""
    status = scheduler.get_status()
    
    if status['enabled'] and status['running']:
        return f"""✅ **Scheduler Active**
📅 Scheduled Time: {status['scheduled_time']} {status['timezone']}
⏰ Next Run: {status['next_run']}
🕐 Current Time: {status['current_time']}"""
    elif status['enabled']:
        return "⚠️ Schedule enabled but not running. Click 'Enable Schedule' to start."
    else:
        return "🛑 Scheduler is disabled"


# =============================================================================
# GRADIO UI
# =============================================================================

def create_app():
    """Create unified Gradio application."""
    
    # Get available TTS voices
    try:
        tts = TTSInference()
        available_voices = tts.get_available_voices()
    except Exception as e:
        print(f"⚠️ TTS not available: {e}")
        available_voices = ["Sadaltager", "Aoede", "Charon", "Fenrir", "Kore", "Puck"]
    
    # Detect system timezone
    try:
        local_tz = str(datetime.now().astimezone().tzinfo)
    except:
        local_tz = "Etc/UTC"
    
    with gr.Blocks(
        title="Reddit AI Analyzer", 
        theme=gr.themes.Soft(),
        css="""
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }
        textarea, input, .output-text {
            font-feature-settings: normal !important;
            text-rendering: optimizeLegibility !important;
        }
        """
    ) as demo:
        
        gr.Markdown("# 🤖 Reddit AI Analyzer")
        gr.Markdown(
            "Analyze Reddit posts and comments using AI to extract insights and trends. "
            "Run analysis now or schedule it to run automatically!"
        )
        
        # === MAIN CONFIGURATION ===
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📝 Analysis Configuration")
                
                subreddit = gr.Textbox(
                    label="Subreddit Configuration",
                    value=format_subreddit_config(DEFAULT_SUBREDDIT_CONFIG),
                    placeholder="LocalLlaMA:10, artificial:5, MachineLearning:2",
                    info="Format: SubredditName:PostLimit, SubredditName2:PostLimit"
                )
                
                time_filter = gr.Dropdown(
                    label="Time Filter",
                    choices=["hour", "day", "week", "month", "year", "all"],
                    value=DEFAULT_TIME_FILTER.value,
                    info="Time period for top posts"
                )
                
                with gr.Row():
                    top_comments = gr.Number(
                        label="Top Comments",
                        value=DEFAULT_TOP_COMMENTS,
                        minimum=1,
                        maximum=10,
                        step=1
                    )
                    
                    replies = gr.Number(
                        label="Replies per Comment",
                        value=DEFAULT_REPLIES_PER_COMMENT,
                        minimum=1,
                        maximum=5,
                        step=1
                    )
                
                model = gr.Dropdown(
                    label="AI Model",
                    choices=["gemini-2.5-pro", "gemini-2.5-flash", "openai:gpt-4o", "openai:gpt-4o-mini", "openai:gpt-5"],
                    value=DEFAULT_MODEL,
                    info="AI model for analysis"
                )
                
                # ✅ ADD GENERATION CONFIG SECTION
                with gr.Accordion("⚙️ Generation Settings (Advanced)", open=False):
                    max_output_tokens = gr.Slider(
                        label="Max Output Tokens",
                        minimum=1024,
                        maximum=65535,
                        step=1024,
                        value=DEFAULT_MAX_OUTPUT_TOKENS,
                        info="Maximum length of AI response"
                    )
                    
                    temperature = gr.Slider(
                        label="Temperature",
                        minimum=0.0,
                        maximum=2.0,
                        step=0.1,
                        value=DEFAULT_TEMPERATURE,
                        info="Creativity (0=focused, 2=creative)"
                    )
                    
                    with gr.Row():
                        top_p = gr.Slider(
                            label="Top P",
                            minimum=0.0,
                            maximum=1.0,
                            step=0.05,
                            value=DEFAULT_TOP_P,
                            info="Nucleus sampling"
                        )
                        
                        top_k = gr.Slider(
                            label="Top K",
                            minimum=1,
                            maximum=100,
                            step=1,
                            value=DEFAULT_TOP_K,
                            info="Top-k sampling (Gemini only)"
                        )
                    
                    thinking_budget = gr.Slider(
                        label="Thinking Budget (ms)",
                        minimum=100,
                        maximum=32768,
                        step=100,
                        value=DEFAULT_THINKING_BUDGET,
                        info="Time budget for AI thinking (Gemini only)"
                    )
                    
                    gr.Markdown("""
                    **💡 Tips:**
                    - **Max Tokens:** Higher = longer responses (use 8192+ for detailed analysis)
                    - **Temperature:** 0.7-1.0 for balanced, 1.0-2.0 for creative
                    - **Top P:** 0.9-0.95 recommended
                    - **Top K:** 40-100 for variety, lower for focused
                    - **Thinking Budget:** 500-2000ms for complex tasks
                    """)
                
                # Auto-update max tokens based on model
                def update_max_tokens(model_name):
                    max_val = MODEL_MAX_TOKENS.get(model_name, 8192)
                    return gr.update(maximum=max_val, value=min(DEFAULT_MAX_OUTPUT_TOKENS, max_val))
                
                model.change(
                    fn=update_max_tokens,
                    inputs=[model],
                    outputs=[max_output_tokens]
                )
            
            with gr.Column():
                gr.Markdown("### 🎯 Analysis Criteria")
                
                # === SYSTEM PROMPT (ALWAYS VISIBLE, SCROLLABLE) ===
                system_prompt = gr.Textbox(
                    label="System Prompt",
                    value=DEFAULT_SYSTEM_PROMPT,
                    lines=8,
                    max_lines=8,  # Fixed height, forces scroll
                    info="Instructions for how the AI should analyze",
                    show_copy_button=True,
                    interactive=True
                )
                
                # === USER PROMPT (ALWAYS VISIBLE, SCROLLABLE) ===
                user_prompt = gr.Textbox(
                    label="User Prompt",
                    value=DEFAULT_USER_PROMPT,
                    lines=8,
                    max_lines=8,  # Fixed height, forces scroll
                    info="Tell the AI what insights you're looking for",
                    show_copy_button=True,
                    interactive=True
                )
                
                send_telegram = gr.Checkbox(
                    label="📱 Send results to Telegram",
                    value=False,
                    info="Send analysis file to your Telegram bot"
                )
        
        # === TTS SECTION ===
        gr.Markdown("### 🎙️ Text-to-Speech (Optional)")
        
        generate_tts = gr.Checkbox(
            label="🎤 Generate Audio Narration",
            value=False,
            info="Generate audio narration of analysis"
        )
        
        with gr.Group(visible=False) as tts_group:
            with gr.Row():
                tts_model = gr.Dropdown(
                    label="TTS Model",
                    choices=["gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"],
                    value="gemini-2.5-flash-preview-tts"
                )
                
                voice_name = gr.Dropdown(
                    label="Voice",
                    choices=available_voices,
                    value="Sadaltager"
                )
            
            tone_instructions = gr.Textbox(
                label="Voice Tone Instructions",
                value="Speak in engaging and excited tone",
                info="Instructions for voice tone/style"
            )
        
        generate_tts.change(
            fn=lambda x: gr.update(visible=x),
            inputs=[generate_tts],
            outputs=[tts_group]
        )
        
        # === EMAIL SECTION ===
        gr.Markdown("### 📧 Email Newsletter Integration (Optional)")
        
        fetch_emails = gr.Checkbox(
            label="📬 Fetch & Analyze AI News Emails",
            value=False,
            info="Include email newsletters in analysis alongside Reddit data"
        )
        
        with gr.Group(visible=False) as email_group:
            with gr.Row():
                email_address = gr.Textbox(
                    label="Email Address",
                    value=EMAIL_ADDRESS,
                    placeholder="your.email@gmail.com"
                )
                
                email_password = gr.Textbox(
                    label="App Password",
                    value=EMAIL_PASSWORD,
                    type="password",
                    info="Gmail App Password"
                )
            
            allowed_senders = gr.Textbox(
                label="Allowed Senders",
                value=", ".join(DEFAULT_ALLOWED_SENDERS),
                placeholder="thebatch@deeplearning.ai, newsletter@openai.com",
                info="Comma-separated list"
            )
            
            with gr.Row():
                email_hours = gr.Number(
                    label="Hours Back",
                    value=DEFAULT_EMAIL_HOURS_BACK,
                    minimum=1,
                    maximum=8760,  # 365 days (1 year)
                    info="How many hours back to search (max 1 year)"
                )
                
                max_emails = gr.Number(
                    label="Max Emails",
                    value=DEFAULT_MAX_EMAILS,
                    minimum=1,
                    maximum=200,  # More emails
                    info="Maximum emails to fetch"
                )
        
        fetch_emails.change(
            fn=lambda x: gr.update(visible=x),
            inputs=[fetch_emails],
            outputs=[email_group]
        )
        
        # === SCHEDULE SECTION ===
        gr.Markdown("### ⏰ Automatic Schedule (Optional)")
        gr.Markdown(f"**System Timezone:** {local_tz}")
        
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    schedule_hour = gr.Number(
                        label="Hour (24h)",
                        value=DEFAULT_SCHEDULE_HOUR,
                        minimum=0,
                        maximum=23,
                        step=1
                    )
                    
                    schedule_minute = gr.Number(
                        label="Minute",
                        value=DEFAULT_SCHEDULE_MINUTE,
                        minimum=0,
                        maximum=59,
                        step=1
                    )
                
                schedule_timezone = gr.Textbox(
                    label="Timezone",
                    value=local_tz,
                    placeholder="America/New_York, Europe/London, Etc/UTC"
                )
                
                with gr.Row():
                    enable_btn = gr.Button("✅ Enable Schedule", variant="primary")
                    disable_btn = gr.Button("🛑 Disable Schedule", variant="stop")
                    refresh_btn = gr.Button("🔄 Refresh Status")
            
            with gr.Column():
                schedule_status = gr.Textbox(
                    label="Schedule Status",
                    value=get_schedule_status(),
                    interactive=False,
                    lines=5
                )
        
        # === RUN BUTTON ===
        gr.Markdown("---")
        run_btn = gr.Button("▶️ Run Analysis Now", variant="primary", size="lg")
        result = gr.Textbox(label="Result", interactive=False, lines=3)
        
        # === OUTPUT DISPLAY ===
        with gr.Row():
            content = gr.Textbox(
                label="Analysis Output",
                interactive=False,
                lines=20,
                max_lines=30,
                show_copy_button=True,
                visible=False
            )
        
        with gr.Row():
            download = gr.File(label="📄 Analysis", visible=False)
            raw_download = gr.File(label="📊 Raw Data", visible=False)
            audio_download = gr.File(label="🎙️ Audio", visible=False)
            email_download = gr.File(label="📧 Emails", visible=False)
            llm_download = gr.File(label="🧠 LLM Input", visible=False)
        
        # === EVENT HANDLERS ===
        
        # Run analysis
        run_btn.click(
            fn=run_manual_analysis,
            inputs=[
                subreddit, time_filter, top_comments, replies,
                model, system_prompt, user_prompt, send_telegram,
                generate_tts, tts_model, voice_name, tone_instructions,
                fetch_emails, email_address, email_password, allowed_senders,
                email_hours, max_emails,
                max_output_tokens, temperature, top_p, top_k, thinking_budget  # ✅ Add thinking_budget
            ],
            outputs=[
                result, content, download, raw_download,
                audio_download, email_download, llm_download
            ]
        ).then(
            fn=lambda c, f, r, a, e, l: (
                gr.update(visible=c is not None),
                gr.update(visible=f is not None),
                gr.update(visible=r is not None),
                gr.update(visible=a is not None),
                gr.update(visible=e is not None),
                gr.update(visible=l is not None)
            ),
            inputs=[content, download, raw_download, audio_download, email_download, llm_download],
            outputs=[content, download, raw_download, audio_download, email_download, llm_download]
        )
        
        # Enable schedule
        enable_btn.click(
            fn=enable_schedule,
            inputs=[
                schedule_hour, schedule_minute, schedule_timezone,
                subreddit, time_filter, top_comments, replies,
                model, system_prompt, user_prompt,
                generate_tts, tts_model, voice_name, tone_instructions,
                fetch_emails, email_address, email_password, allowed_senders,
                email_hours, max_emails,
                max_output_tokens, temperature, top_p, top_k, thinking_budget  # ✅ Add thinking_budget
            ],
            outputs=[schedule_status]
        )
        
        # Disable schedule
        disable_btn.click(
            fn=disable_schedule,
            outputs=[schedule_status]
        )
        
        # Refresh status
        refresh_btn.click(
            fn=get_schedule_status,
            outputs=[schedule_status]
        )
        
        gr.Markdown("""
        ### 📋 Quick Guide
        
        **Run Now:** Configure settings and click "▶️ Run Analysis Now"
        
        **Schedule:** Set time/timezone and click "✅ Enable Schedule" to run daily automatically
        
        **Notes:**
        - Scheduled runs always send results to Telegram
        - Schedule persists across restarts
        - All files saved to `outputs/` folder
        """)
    
    return demo


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    initialize_scheduler()
    demo = create_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )