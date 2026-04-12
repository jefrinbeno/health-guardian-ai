from .google_services import GoogleHealthService

class HealthGuardian:
    """
    Core logic for the Health & Wellness dynamic assistant.
    Analyzes context to provide proactive health interventions.
    """
    def __init__(self):
        self.service = GoogleHealthService()
        self.SEDENTARY_THRESHOLD = 120  # Max minutes allowed without movement

    def analyze_wellbeing(self, user_context):
        """
        Decision Logic: Analyzes activity vs. schedule.
        """
        activity_minutes = self.service.get_last_activity_duration()
        is_in_meeting = self.service.check_calendar_conflicts()
        is_working = user_context.get("is_working", False)

        # Logic 1: If in a meeting, do not interrupt.
        if is_in_meeting:
            return "Status: Do Not Disturb (In Meeting)."

        # Logic 2: If sedentary for too long while working, trigger intervention.
        if activity_minutes >= self.SEDENTARY_THRESHOLD and is_working:
            return self._generate_intervention("stretch_break")
        
        return "You're doing great! Keep staying hydrated."

    def _generate_intervention(self, type):
        interventions = {
            "stretch_break": "⚠️ Alert: You've been sitting for over 2 hours. Take 5 mins to stretch your legs!",
            "hydration": "💧 Reminder: Time for a water break based on your routine."
        }
        return interventions.get(type, "Keep it up!")

# Quick test execution
if __name__ == "__main__":
    assistant = HealthGuardian()
    # Simulating a user who is currently working
    context = {"is_working": True}
    print(assistant.analyze_wellbeing(context))