import pytest
from src.assistant import HealthGuardian

def test_sedentary_logic(monkeypatch):
    """TESTING: Verify alert triggers only when working and threshold met."""
    app = HealthGuardian()
    
    # Mock the Google Service so we don't need real API keys for the test
    monkeypatch.setattr(app.service, 'get_last_activity_duration', lambda: 150)
    monkeypatch.setattr(app.service, 'check_calendar_conflicts', lambda: False)
    
    result = app.analyze_wellbeing({"is_working": True})
    assert "Alert dispatched" in result