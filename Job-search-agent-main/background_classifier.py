import time
import schedule
import json
import pandas as pd
from datetime import datetime
from fetcher_email import authenticate_gmail, fetch_latest_unread_emails
from classify_gemini import classify_emails_with_gemini

class EmailClassifierService:
    def __init__(self):
        self.service = authenticate_gmail()
        self.results_file = "email_results.json"
        self.processed_ids_file = "processed_ids.json"
        self.last_processed_emails = self.load_processed_ids()

    def load_processed_ids(self):
        try:
            with open(self.processed_ids_file, 'r') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()
    def save_processed_ids(self):
        try:
            with open(self.processed_ids_file, 'w') as f:
                json.dump(list(self.last_processed_emails), f)
        except Exception as e:
            print(f"Error saving processed email IDs: {e}")

    def process_emails(self):
        """Main processing function"""
        print(f"[{datetime.now()}] Starting email classification...")
        
        try:
            # Fetch emails
            emails = fetch_latest_unread_emails(self.service, max_results=10)
            
            if not emails:
                print("No unread emails found.")
                return
            
            # Filter out already processed emails
            new_emails = [email for email in emails if email['id'] not in self.last_processed_emails]
            
            if not new_emails:
                print("No new emails to process.")
                return
            
            print(f"Processing {len(new_emails)} new emails...")
            
            # Classify emails
            labels = classify_emails_with_gemini(new_emails)
            
            # Add labels to email data
            for email, label in zip(new_emails, labels):
                email["label"] = label
                email["processed_at"] = datetime.now().isoformat()
            
            # Save results
            self.save_results(new_emails)
            
            # Update processed emails set
            self.last_processed_emails.update([email['id'] for email in new_emails])
            self.save_processed_ids()

            print(f"Successfully processed {len(new_emails)} emails.")
            
        except Exception as e:
            print(f"Error processing emails: {e}")
    
    def save_results(self, new_emails):
        """Save results to JSON file"""
        try:
            # Load existing results
            try:
                with open(self.results_file, 'r') as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = []
            
            # Add new results
            existing_data.extend(new_emails)
            
            # Keep only last 100 emails to prevent file from growing too large
            existing_data = existing_data[-100:]
            
            # Save updated results
            with open(self.results_file, 'w') as f:
                json.dump(existing_data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def get_latest_results(self):
        """Get latest results for dashboard"""
        try:
            with open(self.results_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def run_scheduler(self):
        """Run the scheduler"""
        # Schedule email processing every 30 minutes
        schedule.every(1).minutes.do(self.process_emails)
        
        # Also run once immediately
        self.process_emails()
        
        print("Email classifier service started. Press Ctrl+C to stop.")
        print("Processing emails every 30 minutes...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nService stopped.")

if __name__ == "__main__":
    service = EmailClassifierService()
    service.run_scheduler()