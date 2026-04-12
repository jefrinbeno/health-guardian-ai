import unittest
from src.assistant import HealthGuardian

class TestHealthGuardian(unittest.TestCase):
    """
    Unit tests to validate the decision-making logic of the Health Guardian.
    """
    def setUp(self):
        self.assistant = HealthGuardian()

    def test_do_not_disturb_during_meetings(self):
        # Mocking: Force the calendar to say we are in a meeting
        self.assistant.service.check_calendar_conflicts = lambda: True
        
        result = self.assistant.analyze_wellbeing({"is_working": True})
        self.assertEqual(result, "Status: Do Not Disturb (In Meeting).")

    def test_sedentary_intervention_triggers(self):
        # Mocking: No meeting, but user hasn't moved in 150 minutes
        self.assistant.service.check_calendar_conflicts = lambda: False
        self.assistant.service.get_last_activity_duration = lambda: 150
        
        result = self.assistant.analyze_wellbeing({"is_working": True})
        # Check if the alert phrase is in the response
        self.assertTrue("stretch" in result.lower() or "alert" in result.lower())

    def test_healthy_status_returns_positive(self):
        # Mocking: No meeting, user moved 30 minutes ago
        self.assistant.service.check_calendar_conflicts = lambda: False
        self.assistant.service.get_last_activity_duration = lambda: 30
        
        result = self.assistant.analyze_wellbeing({"is_working": True})
        self.assertTrue("great" in result.lower())

if __name__ == '__main__':
    unittest.main()