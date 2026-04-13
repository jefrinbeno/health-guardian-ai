import os
import datetime
import pickle
from functools import lru_cache
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# These are the permissions we are asking the user for
# We added the Tasks API scope!
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/tasks' 
]

class GoogleHealthService:
    def __init__(self):
        print("Initiating Live Google Cloud Connection...")
        self.creds = self._authenticate()
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        self.fitness_service = build('fitness', 'v1', credentials=self.creds)
        # Added the Tasks API builder here!
        self.tasks_service = build('tasks', 'v1', credentials=self.creds) 

    def _authenticate(self):
        """Handles OAuth 2.0 flow and token caching."""
        creds = None
        # Check if we already logged in previously
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If no valid credentials, pop open the browser to log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # This explicitly looks for the file you just downloaded!
                flow = InstalledAppFlow.from_client_secrets_file(
                    'src/client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials so we don't have to log in every single time
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
            
            # Check if a meeting is happening RIGHT NOW
            current_time = datetime.datetime.now(datetime.timezone.utc)
            for event in events:
                start_str = event['start'].get('dateTime', event['start'].get('date'))
                end_str = event['end'].get('dateTime', event['end'].get('date'))
                if 'T' not in start_str: # Skip all-day events
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
        """
        Fetches activity data. 
        """
        # For the hackathon demo, we will simulate the sedentary trigger here 
        # so you don't have to go run around the block with a smartwatch to test it!
        return 150

    # Add this new function at the very bottom of the file!
    def create_health_task(self, title="Mandatory Health Walk", notes="Scheduled by Health Guardian AI due to burnout risk."):
        """Writes a new task directly to the user's Google Tasks."""
        try:
            task = {
                'title': title,
                'notes': notes
            }
            # '@default' targets the user's primary task list
            result = self.tasks_service.tasks().insert(tasklist='@default', body=task).execute()
            print(f"Task created successfully: {result.get('title')}")
            return True
        except Exception as e:
            print(f"Failed to create Google Task: {e}")
            return False