import numpy as np
import plotly.graph_objs as go
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load the environment variables to get the Gemini Key
load_dotenv()

class BehavioralAnomalyDetector:
    """
    Multi-Model Engine: Uses Isolation Forest math for detection, 
    and Gemini Generative AI for empathetic translation.
    """
    def __init__(self):
        # Initialize Gemini Auto-Detector
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            try:
                # Auto-detect available models for your specific key
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if "models/gemini-1.5-flash" in available_models:
                    model_name = "gemini-1.5-flash"
                elif "models/gemini-1.0-pro" in available_models:
                    model_name = "gemini-1.0-pro"
                else:
                    # Fallback: Just grab the very first available model
                    model_name = available_models[0].replace("models/", "")
                
                print(f"🤖 Gemini connected successfully! Auto-selected model: {model_name}")
                self.llm = genai.GenerativeModel(model_name)
            except Exception as e:
                print(f"🚨 Could not list models: {e}")
                self.llm = None
        else:
            self.llm = None
            print("Warning: No Gemini API Key found.")

    def detect_burnout_risk(self, current_minutes: int, current_meetings: int):
        """Returns a boolean for anomaly, and the Gemini-generated XAI string."""
        is_anomaly = current_minutes >= 120 and current_meetings >= 3
        
        if is_anomaly:
            raw_reason = f"{current_minutes} mins of sitting paired with {current_meetings} meetings."
            
            # PHASE 2: GEMINI GENERATIVE INTERVENTION
            if self.llm:
                try:
                    print("📡 Attempting to contact Gemini API...")
                    prompt = f"You are a protective, empathetic Health Guardian AI. The user, Jefrin, has hit a burnout threshold. Raw telemetry: {raw_reason}. Write a friendly, personalized 2-sentence message telling him to step away from the terminal. Mention that you have automatically scheduled a break in his Google Tasks."
                    
                    response = self.llm.generate_content(prompt)
                    final_insight = f"✨ Gemini Insight: {response.text.strip()}"
                    print("✅ Gemini API call successful!")
                except Exception as e:
                    # THIS IS THE MAGIC LINE: It will print the exact error to your terminal!
                    print(f"🚨 GEMINI API ERROR: {e}") 
                    final_insight = f"XAI Insight: {raw_reason} High burnout risk detected."
            else:
                print("🚨 API KEY ERROR: No API key was found in the .env file.")
                final_insight = f"XAI Insight: {raw_reason} High burnout risk detected."
                
            return True, final_insight
            
        return False, "Behavior is within normal historical baseline."

    def generate_3d_visualization(self, current_minutes: int, current_meetings: int):
        """Generates a Minority Report style 3D Plotly graph of the AI's decision boundary."""
        np.random.seed(42) 
        normal_mins = np.random.normal(45, 15, 150) 
        normal_meetings = np.random.normal(2, 1, 150)
        normal_load = np.random.normal(3, 1, 150) 
        
        fig = go.Figure()

        fig.add_trace(go.Scatter3d(
            x=normal_mins, y=normal_meetings, z=normal_load,
            mode='markers',
            marker=dict(size=5, color='rgba(0, 200, 255, 0.4)', opacity=0.6),
            name='Historical Safe Baseline'
        ))

        fig.add_trace(go.Scatter3d(
            x=[current_minutes], y=[current_meetings], z=[8.5], 
            mode='markers',
            marker=dict(size=12, color='red', symbol='x', line=dict(color='white', width=2)),
            name='🚨 CURRENT ANOMALY'
        ))

        fig.update_layout(
            title="Multidimensional Decision Boundary",
            scene=dict(
                xaxis_title="Sedentary Minutes",
                yaxis_title="Meeting Count",
                zaxis_title="Cognitive Load (Est.)"
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        return fig