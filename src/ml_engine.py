import numpy as np
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger(__name__)

class BehavioralAnomalyDetector:
    def __init__(self):
        logger.info("Initializing ML Model: Isolation Forest...")
        # Contamination=0.1 means we expect about 10% of days to be "burnout" days
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self._train_baseline()

    def _train_baseline(self):
        """
        Simulates 2 weeks of historical health/calendar data.
        Format: [Consecutive_Sitting_Minutes, Total_Meetings_Today]
        """
        # Normal days: ~60-100 mins sitting before a break, 1-3 meetings
        historical_data = np.array([
            [60, 2], [75, 3], [90, 1], [85, 2], [100, 3], 
            [110, 4], [70, 1], [95, 2], [105, 3], [80, 2],
            [150, 6], # Example of a past highly stressful anomaly day
        ])
        self.model.fit(historical_data)
        logger.info("Baseline behavioral model trained.")

    def detect_burnout_risk(self, current_minutes: int, current_meetings: int) -> tuple[bool, str]:
        """
        Analyzes live data against the baseline. 
        Returns (Is_Anomaly, Explainable_AI_Reason)
        """
        # Predict returns -1 for anomaly, 1 for normal
        prediction = self.model.predict([[current_minutes, current_meetings]])
        is_anomaly = prediction[0] == -1
        
        if is_anomaly:
            reason = f"XAI Insight: {current_minutes} mins of sitting paired with {current_meetings} meetings deviates significantly from your baseline. High burnout risk detected."
            return True, reason
            
        return False, "Routine looks normal."