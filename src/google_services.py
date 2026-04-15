import os
import datetime
import pickle
import base64
from email.message import EmailMessage
from functools import lru_cache
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# The Perfect LPA (Least Privilege Access) Scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/spreadsheets', # Added Sheets
    'https://www.googleapis.com/auth/gmail.send'    # Added Gmail (Send Only)
]

class GoogleHealthService:
    def __init__(self):
        print("Initiating Live Google Cloud Connection...")
        self.creds = self._authenticate()
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        self.fitness_service = build('fitness', 'v1', credentials=self.creds)
        self.tasks_service = build('tasks', 'v1', credentials=self.creds) 
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)

    def _authenticate(self):
        """Handles OAuth 2.0 flow and token caching."""
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'src/client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    @lru_cache(maxsize=32)
    def check_calendar_conflicts(self):
        """Fetches live events from your actual Google Calendar."""
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.calendar_service.events().list(
                calendarId='primary', timeMin=now, maxResults=3, 
                singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                return False
            
            current_time = datetime.datetime.now(datetime.timezone.utc)
            for event in events:
                start_str = event['start'].get('dateTime', event['start'].get('date'))
                end_str = event['end'].get('dateTime', event['end'].get('date'))
                if 'T' not in start_str: 
                    continue 
                    
                start = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                
                if start <= current_time <= end:
                    print("Live Calendar: Meeting detected! Silencing alerts.")
                    return True
            return False
            
        except Exception as e:
            print(f"Calendar API Error: {e}")
            return False

    def get_last_activity_duration(self):
        return 150 # Mock data for the ML trigger

    def create_health_task(self, title="Mandatory Health Walk", notes="Scheduled by Health Guardian AI due to burnout risk."):
        """Writes a new task directly to the user's Google Tasks."""
        try:
            task = {'title': title, 'notes': notes}
            result = self.tasks_service.tasks().insert(tasklist='@default', body=task).execute()
            return True
        except Exception as e:
            print(f"Failed to create Google Task: {e}")
            return False

    def log_anomaly_to_sheet(self, spreadsheet_id, anomaly_reason, minutes):
        """Writes the ML anomaly directly to a live Google Sheet."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = [[timestamp, anomaly_reason, f"{minutes} mins"]]
            body = {'values': data}
            
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range="Sheet1!A:C",
                valueInputOption="USER_ENTERED", body=body).execute()
            print("Successfully logged anomaly to Google Sheets.")
            return True
        except Exception as e:
            print(f"Google Sheets Error: {e}")
            return False

    def send_health_report(self, to_email, report_text):
        """Sends an automated email via Gmail API."""
        try:
            message = EmailMessage()
            message.set_content(report_text)
            message['To'] = to_email
            message['From'] = 'me' # 'me' is a special keyword in Gmail API
            message['Subject'] = '🛡️ Health Guardian AI: Security & Wellness Report'

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}

            self.gmail_service.users().messages().send(userId="me", body=create_message).execute()
            print("Successfully dispatched Gmail report.")
            return True
        except Exception as e:
            print(f"Gmail API Error: {e}")
            return False
    def deploy_calendar_armor(self):
        """Scans tomorrow's schedule and blocks recovery time if meeting-heavy."""
        try:
            # 1. Get tomorrow's time boundaries
            now = datetime.datetime.now(datetime.timezone.utc)
            tomorrow_start = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow_end = tomorrow_start + datetime.timedelta(days=1)
            
            # 2. Fetch tomorrow's meetings
            events_result = self.calendar_service.events().list(
                calendarId='primary', 
                timeMin=tomorrow_start.isoformat(), 
                timeMax=tomorrow_end.isoformat(),
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # 3. The Trigger: 3 or more meetings tomorrow = High Burnout Risk
            if len(events) >= 3: 
                # Find the end time of the LAST meeting of the day
                last_event = events[-1]
                end_str = last_event['end'].get('dateTime', last_event['end'].get('date'))
                
                if 'T' in end_str: # Ensure it's not an all-day event
                    # Calculate a 30-minute Shield Time right after the last meeting
                    shield_start = end_str
                    shield_end_dt = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00')) + datetime.timedelta(minutes=30)
                    shield_end = shield_end_dt.isoformat()
                    
                    # 4. Create the Shield Event
                    shield_event = {
                        'summary': '🛡️ Health Guardian: Focus Shield',
                        'description': 'Automated burnout prevention block. Do not schedule over.',
                        'start': {'dateTime': shield_start},
                        'end': {'dateTime': shield_end},
                        'colorId': '11'  # Red color in Google Calendar
                    }
                    
                    self.calendar_service.events().insert(calendarId='primary', body=shield_event).execute()
                    print("Calendar Armor Deployed successfully.")
                    return True, f"Deployed 30-min Focus Shield tomorrow at {shield_start[-14:-9]}."
            
            return False, f"Tomorrow looks light ({len(events)} meetings). No armor needed."
            
        except Exception as e:
            print(f"Armor Deployment Failed: {e}")
            return False, f"Error: {e}"        