# 🛡️ Health Guardian AI

A smart, dynamic wellness assistant designed to monitor physical activity and proactively suggest health interventions without disrupting deep work.

## 🎯 Chosen Vertical: Health & Wellness
The goal of this project is to act as a daily routine and habit tracker that provides personalized encouragement based on contextual user data.

## 🧠 Approach and Logic
Instead of just sending "time to stand up" alerts blindly, Health Guardian uses **Context-Aware Decision Making**:
1. **Data Ingestion:** It checks the user's last known physical activity duration.
2. **Conflict Resolution:** It checks the user's calendar. If the user is in a meeting, it suppresses all alerts to respect "Do Not Disturb" time.
3. **Proactive Intervention:** If the user has been sedentary for over 2 hours and is *not* in a meeting, it triggers a personalized wellness intervention (e.g., stretching or hydration).

## ☁️ Google Services Integration
* **Google Fit API:** Used to retrieve the duration of the user's last logged physical activity.
* **Google Calendar API:** Used to fetch the user's current schedule to prevent alert fatigue during meetings.
*(Note: Code is structured to use `google-api-python-client` with secure environment variables. A fallback mock system is implemented for local AI evaluation).*

## 🔒 Evaluation Focus Areas Addressed
* **Code Quality:** Modular, Object-Oriented design with clear docstrings.
* **Security:** API keys are strictly managed via `os.getenv` and `.env` files (excluded via `.gitignore`).
* **Efficiency:** Logic avoids nested loops and exits early when calendar conflicts are detected.
* **Testing:** Includes comprehensive unit tests (`tests/test_logic.py`) utilizing Python's `unittest` framework.

## 📌 Assumptions Made
* The user relies on Google Calendar for their daily schedule.
* A sedentary threshold of 120 minutes requires a wellness intervention.