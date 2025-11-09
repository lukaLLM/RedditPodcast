"""Test email fetching and parsing."""
from email_fetcher import EmailFetcher
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from pathlib import Path
import sys

if __name__ == "__main__":
    # Validate configuration
    print("🔍 Validating configuration...")
    
    if not EMAIL_ADDRESS:
        print("❌ EMAIL_ADDRESS is not set in .env file")
        print("   Add: EMAIL_ADDRESS=your.email@gmail.com")
        sys.exit(1)
    
    if not EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD is not set in .env file")
        print("   Add: EMAIL_PASSWORD=your_app_password")
        print("   Create App Password at: https://myaccount.google.com/apppasswords")
        sys.exit(1)
    
    print(f"✅ Email: {EMAIL_ADDRESS}")
    print(f"✅ Password: {'*' * len(EMAIL_PASSWORD)} (length: {len(EMAIL_PASSWORD)})")
    
    # Test connection
    print("\n🔍 Testing email connection...")
    fetcher = EmailFetcher(EMAIL_ADDRESS, EMAIL_PASSWORD)
    
    print("\n📧 Fetching emails from thebatch@deeplearning.ai...")
    emails = fetcher.fetch_emails(
        allowed_senders=["thebatch@deeplearning.ai"],
        hours_back=168,  # 1 week
        max_emails=1
    )
    
    if emails:
        print(f"\n✅ Found {len(emails)} email(s)\n")
        
        # Display formatted output
        formatted = fetcher.format_emails_for_analysis(emails, max_length=None)
        print(formatted)
        print(f"\nTotal formatted length: {len(formatted)} characters")
        
        # Save to files for inspection
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Save formatted text
        text_file = output_dir / "test_email_parsed.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(f"\n💾 Saved parsed text to: {text_file}")
        
        # Also show first 1000 chars for quick inspection
        print("\n" + "="*80)
        print("PREVIEW (first 1000 chars):")
        print("="*80)
        print(emails[0]['body'][:1000])
        print("="*80)
        
    else:
        print("❌ No emails found")
        print("\n💡 Troubleshooting:")
        print("1. Verify EMAIL_ADDRESS and EMAIL_PASSWORD in .env")
        print("2. For Gmail, use an App Password (16 characters, no spaces)")
        print("   Create at: https://myaccount.google.com/apppasswords")
        print("3. Enable IMAP in Gmail Settings → Forwarding and POP/IMAP")
        print("4. Check if you have emails from thebatch@deeplearning.ai")
        print("5. Try with a different sender email address")