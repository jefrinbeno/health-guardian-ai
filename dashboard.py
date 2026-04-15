import streamlit as st
import requests
# Import the ML engine for the 3D visualizer!
from src.ml_engine import BehavioralAnomalyDetector

# 1. UI Configuration
st.set_page_config(page_title="Health Guardian AI", page_icon="🛡️", layout="centered")

st.title("🛡️ Health Guardian Command Center")
st.markdown("---")

# 2. Status Indicators
col1, col2 = st.columns(2)
with col1:
    st.success("🟢 API Backend: ONLINE")
with col2:
    st.info("📡 Google Cloud: CONNECTED")

st.markdown("### System Controls")
is_working = st.checkbox("Toggle Deep Work Mode", value=True)

# 3. The Execution Button
if st.button("Run Live Health Analysis", type="primary"):
    with st.spinner("Pinging Live Google Cloud & Machine Learning APIs..."):
        try:
            # Send the request to your local FastAPI server
            response = requests.post(
                "http://127.0.0.1:8000/api/analyze",
                json={"is_working": is_working}
            )
            data = response.json()
            
            if data.get("status") == "success":
                # Display the AI's decision
                st.write("### 🧠 AI Decision:")
                
                analysis_text = data["analysis"]
                # Display the correct colored box based on the response
                if "ALERT" in analysis_text or "Anomaly" in analysis_text:
                    st.error(analysis_text)
                elif "Do Not Disturb" in analysis_text:
                    st.warning(analysis_text)
                else:
                    st.success(analysis_text)
                
                # --- NEW: LIVE AI TELEMETRY GRAPH ---
                st.markdown("### 📡 Live AI Telemetry")
                
                # Initialize the brain just for the visual
                ml_brain = BehavioralAnomalyDetector()
                
                # Pass in the hardcoded anomaly triggers we used (150 mins, 4 meetings)
                fig = ml_brain.generate_3d_visualization(150, 4)
                
                # Render the interactive 3D chart!
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error("Backend error analyzing data.")
                
        except Exception as e:
            st.error("Backend offline. Make sure your FastAPI server is running!")
st.markdown("---")
# The Predictive Shield Button
if st.button("Deploy Predictive Calendar Armor", type="secondary"):
    with st.spinner("Scanning tomorrow's timeline..."):
        try:
            response = requests.post("http://127.0.0.1:8000/api/predict")
            data = response.json()
            
            if "ARMOR ACTIVE" in data["analysis"]:
                st.success(data["analysis"])
            else:
                st.info(data["analysis"])
        except Exception as e:
            st.error("Backend offline. Make sure your FastAPI server is running!")
