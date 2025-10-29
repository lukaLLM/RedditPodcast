"""
Simple background scheduler for daily analysis.
"""
import asyncio
import json
import threading
from datetime import datetime, time, timedelta
from pathlib import Path
import zoneinfo
from typing import Optional, Dict

from config import SCHEDULE_CONFIG_FILE


class SimpleScheduler:
    """Simple daily scheduler that runs in background thread."""
    
    def __init__(self, config_file: str = SCHEDULE_CONFIG_FILE):
        self.config_file = Path(config_file)
        self.enabled = False
        self.hour = 9
        self.minute = 0
        self.timezone = "Etc/UTC"
        self.config = {}
        self.loop = None
        self.thread = None
        self.stop_event = threading.Event()
        
    def load_config(self) -> dict:
        """Load schedule configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.enabled = data.get('enabled', False)
                    self.hour = data.get('hour', 9)
                    self.minute = data.get('minute', 0)
                    self.timezone = data.get('timezone', 'Etc/UTC')
                    self.config = data.get('config', {})
                    print(f"✅ Loaded schedule: {self.hour:02d}:{self.minute:02d} {self.timezone}")
                    return data
        except Exception as e:
            print(f"⚠️ Failed to load schedule config: {e}")
        return {}
    
    def save_config(self, enabled: bool, hour: int, minute: int, 
                    timezone: str, config: dict) -> bool:
        """Save schedule configuration to file."""
        try:
            data = {
                "enabled": enabled,
                "hour": hour,
                "minute": minute,
                "timezone": timezone,
                "config": config
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.enabled = enabled
            self.hour = hour
            self.minute = minute
            self.timezone = timezone
            self.config = config
            
            print(f"💾 Saved schedule: {hour:02d}:{minute:02d} {timezone} (enabled: {enabled})")
            return True
        except Exception as e:
            print(f"❌ Failed to save schedule config: {e}")
            return False
    
    async def run_analysis(self):
        """Run the Reddit analysis with saved configuration."""
        print(f"🚀 Starting scheduled analysis at {datetime.now()}")
        
        try:
            # Import here to avoid circular imports
            from workflow import run_complete_workflow
            
            # Parse subreddit config
            from utils import parse_subreddit_config
            subreddit_dict = parse_subreddit_config(
                self.config.get('subreddit_config', '')
            )
            
            if not subreddit_dict:
                print("⚠️ No subreddits configured")
                return
            
            # Run workflow
            await run_complete_workflow(
                subreddit_config=subreddit_dict,
                time_filter=self.config.get('time_filter', 'day'),
                top_comments=int(self.config.get('top_comments', 10)),
                replies_per_comment=int(self.config.get('replies_per_comment', 5)),
                model=self.config.get('model', 'gemini-2.5-pro'),
                system_prompt=self.config.get('system_prompt', ''),
                user_prompt=self.config.get('user_prompt', ''),
                send_to_telegram=True
            )
            
            print(f"✅ Scheduled analysis completed")
            
        except Exception as e:
            print(f"❌ Error in scheduled analysis: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to send error to Telegram
            try:
                from telegram_sender import send_error_notification
                await send_error_notification(str(e))
            except:
                pass
    
    async def scheduler_loop(self):
        """Main scheduler loop that checks time every minute."""
        print(f"⏰ Scheduler started (checking every 60s)")
        
        while not self.stop_event.is_set():
            try:
                if self.enabled:
                    # Get current time in configured timezone
                    tz = zoneinfo.ZoneInfo(self.timezone)
                    now = datetime.now(tz)
                    
                    # Check if it's time to run
                    if now.hour == self.hour and now.minute == self.minute:
                        print(f"⏰ Scheduled time reached: {now}")
                        await self.run_analysis()
                        
                        # Sleep for 60 seconds to avoid running multiple times
                        await asyncio.sleep(60)
                
                # Wait 60 seconds before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self.thread and self.thread.is_alive():
            print("⚠️ Scheduler already running")
            return
        
        self.stop_event.clear()
        
        def run_scheduler():
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            try:
                self.loop.run_until_complete(self.scheduler_loop())
            except Exception as e:
                print(f"❌ Scheduler thread error: {e}")
            finally:
                self.loop.close()
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
        print("✅ Scheduler thread started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.thread and self.thread.is_alive():
            print("🛑 Stopping scheduler...")
            self.stop_event.set()
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=5)
            print("✅ Scheduler stopped")
    
    def restart(self):
        """Restart the scheduler with new configuration."""
        self.stop()
        self.start()
    
    def get_status(self) -> dict:
        """Get current scheduler status."""
        is_running = self.thread and self.thread.is_alive()
        
        if self.enabled and is_running:
            tz = zoneinfo.ZoneInfo(self.timezone)
            now = datetime.now(tz)
            next_run = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
            
            # If scheduled time has passed today, next run is tomorrow
            if now.time() > time(self.hour, self.minute):
                next_run += timedelta(days=1)
            
            return {
                "enabled": True,
                "running": True,
                "scheduled_time": f"{self.hour:02d}:{self.minute:02d}",
                "timezone": self.timezone,
                "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z")
            }
        else:
            return {
                "enabled": self.enabled,
                "running": is_running,
                "scheduled_time": f"{self.hour:02d}:{self.minute:02d}" if self.enabled else "Not set",
                "timezone": self.timezone,
                "message": "Scheduler not enabled" if not self.enabled else "Scheduler stopped"
            }


# Global scheduler instance
scheduler = SimpleScheduler()


def initialize_scheduler():
    """Initialize scheduler on app startup."""
    print("🔧 Initializing scheduler...")
    
    # Load saved configuration
    scheduler.load_config()
    
    # Start scheduler if enabled
    if scheduler.enabled:
        scheduler.start()
        print(f"✅ Scheduler started: {scheduler.hour:02d}:{scheduler.minute:02d} {scheduler.timezone}")
    else:
        print("ℹ️ Scheduler disabled (enable in UI)")