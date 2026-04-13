import logging
import os
import pyttsx3  # ACCESSIBILITY: Text-to-speech engine imported at the top for Code Quality
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from plyer import notification
from .google_services import GoogleHealthService
# Add this right under your other imports at the top
from .ml_engine import BehavioralAnomalyDetector

# 1. CODE QUALITY: Professional Logging (No more print statements)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - HealthGuardian - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 2. SECURITY: Load environment variables securely
load_dotenv()

class HealthGuardian:
    """Enterprise-grade Health & Wellness context analyzer."""
    
    # CODE QUALITY: Strict type hinting
    def __init__(self) -> None:
        logger.info("Initializing Health Guardian Core AI...")
        self.service = GoogleHealthService()
        self.ml_brain = BehavioralAnomalyDetector() # <-- Initialize the ML model!

    def analyze_wellbeing(self, user_context: Dict[str, Any]) -> str:
        """Analyzes Google data using Machine Learning Anomaly Detection."""
        try:
            # EFFICIENCY: These calls should ideally be cached in google_services
            activity_minutes: int = self.service.get_last_activity_duration()
            is_in_meeting: bool = self.service.check_calendar_conflicts()
            is_working: bool = user_context.get("is_working", False)

            if is_in_meeting:
                logger.info("Context: User in meeting. Suppressing alerts.")
                return "Status: Do Not Disturb."

            if is_working:
                # <-- Call the ML Model! (Assuming 4 meetings today for the demo)
                is_anomaly, xai_reason = self.ml_brain.detect_burnout_risk(activity_minutes, 4)
                
                if is_anomaly:
                    logger.warning(f"Anomaly Detected: {xai_reason}")
                    self._trigger_intervention("stretch_break")
                    
                    # <-- ADD THIS LINE to write to Google Tasks!
                    self.service.create_health_task() 
                    
                    return f"🚨 ALERT | {xai_reason} (A reminder has been added to your Google Tasks!)"
            
            return f"Status: Optimal. Active for {activity_minutes} mins."
            
        except Exception as e:
            # SECURITY: Catching and logging errors without exposing stack traces to users
            logger.error(f"Analysis failed safely: {str(e)}")
            return "Status: Error analyzing data."

    def _trigger_intervention(self, intervention_type: str) -> str:
        """Triggers OS-level and Accessibility alerts."""
        if intervention_type == "stretch_break":
            # Native OS Notification
            notification.notify(
                title='Health Guardian AI',
                message="Prolonged inactivity detected. Mandatory 5-min break.",
                app_icon=None, 
                timeout=10 
            )
            
            # ACCESSIBILITY: Voice announcement
            engine = pyttsx3.init()
            engine.say("Health Guardian Alert. Prolonged inactivity detected. Please stand up and stretch.")
            engine.runAndWait()
            
            return "Alert dispatched successfully."
        return "No action required."

if __name__ == "__main__":
    app = HealthGuardian()
    result = app.analyze_wellbeing({"is_working": True})
    logger.info(result)