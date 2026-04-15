import logging
import os
import pyttsx3  
import speech_recognition as sr # <-- NEW: The AI's Ears
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from plyer import notification
from .google_services import GoogleHealthService
from .ml_engine import BehavioralAnomalyDetector

# 1. CODE QUALITY: Professional Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - HealthGuardian - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 2. SECURITY: Load environment variables securely
load_dotenv()

class HealthGuardian:
    """Enterprise-grade Health & Wellness context analyzer."""
    
    def __init__(self) -> None:
        logger.info("Initializing Health Guardian Core AI...")
        self.service = GoogleHealthService()
        self.ml_brain = BehavioralAnomalyDetector() 

    def listen_for_compliance(self) -> bool:
        """ACCESSIBILITY: Listens for the user to verbally acknowledge the break."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            logger.info("🎙️ Microphone ON: Listening for voice command...")
            # Quickly adjust to background room noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # Listen for a maximum of 5 seconds
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower()
                logger.info(f"🗣️ User said: '{text}'")
                
                # The trigger words
                if "guardian" in text or "break" in text or "yes" in text:
                    return True
            except sr.WaitTimeoutError:
                logger.warning("Voice command timeout. No response heard.")
            except sr.UnknownValueError:
                logger.warning("Could not understand audio.")
            except Exception as e:
                logger.error(f"Microphone error: {e}")
        return False

    def analyze_wellbeing(self, user_context: Dict[str, Any]) -> str:
        """Analyzes Google data using Machine Learning Anomaly Detection."""
        try:
            activity_minutes: int = self.service.get_last_activity_duration()
            is_in_meeting: bool = self.service.check_calendar_conflicts()
            is_working: bool = user_context.get("is_working", False)

            if is_in_meeting:
                return "Status: Do Not Disturb."

            if is_working:
                is_anomaly, xai_reason = self.ml_brain.detect_burnout_risk(activity_minutes, 4)
                
                if is_anomaly:
                    logger.warning(f"Anomaly Detected: {xai_reason}")
                    
                    # 1. Trigger the standard visual/audio alarms
                    self._trigger_intervention("stretch_break")
                    
                    # 2. Write to Tasks, Sheets, and Gmail
                    self.service.create_health_task() 
                    sheet_id = os.getenv("SPREADSHEET_ID")
                    if sheet_id:
                        self.service.log_anomaly_to_sheet(sheet_id, xai_reason, activity_minutes)
                        
                    user_email = os.getenv("USER_EMAIL")
                    if user_email:
                        email_body = f"Health Guardian Alert.\n\nReason: {xai_reason}\nBreak scheduled in Google Tasks."
                        self.service.send_health_report(user_email, email_body)
                    
                    # --- NEW: VOICE COMPLIANCE LOOP ---
                    compliance_met = self.listen_for_compliance()
                    if compliance_met:
                        engine = pyttsx3.init()
                        engine.say("Break acknowledged. Logging compliance to database. Enjoy your rest.")
                        engine.runAndWait()
                        
                        if sheet_id:
                            self.service.log_anomaly_to_sheet(sheet_id, "User Verbally Complied with Break", activity_minutes)
                        
                        return f"🚨 ALERT | {xai_reason} \n\n🎙️ **VOICE COMMAND ACCEPTED: Break acknowledged & logged!**"
                    else:
                        return f"🚨 ALERT | {xai_reason} \n\n⚠️ **No voice compliance detected. Task remains pending.**"
            
            return f"Status: Optimal. Active for {activity_minutes} mins."
            
        except Exception as e:
            logger.error(f"Analysis failed safely: {str(e)}")
            return "Status: Error analyzing data."

    def _trigger_intervention(self, intervention_type: str) -> str:
        if intervention_type == "stretch_break":
            notification.notify(
                title='Health Guardian AI',
                message="Prolonged inactivity detected. Mandatory 5-min break.",
                app_icon=None, 
                timeout=10 
            )
            engine = pyttsx3.init()
            engine.say("Health Guardian Alert. Prolonged inactivity detected. Please stand up and acknowledge.")
            engine.runAndWait()
            return "Alert dispatched successfully."
        return "No action required."

    def run_predictive_scan(self) -> str:
        """Proactively analyzes tomorrow's calendar to prevent burnout."""
        logger.info("Initiating Predictive Calendar Scan...")
        try:
            deployed, message = self.service.deploy_calendar_armor()
            if deployed:
                return f"🛡️ PREDICTIVE ARMOR ACTIVE | {message}"
            else:
                return f"✅ SCHEDULE CLEAR | {message}"
        except Exception as e:
            logger.error(f"Predictive scan failed: {str(e)}")
            return "Error running predictive scan."