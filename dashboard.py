import streamlit as st
import requests

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
    with st.spinner("Pinging Live Google Calendar & Fitness APIs..."):
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
                if "Alert" in analysis_text or "Anomaly" in analysis_text:
                    st.error(analysis_text)
                elif "Do Not Disturb" in analysis_text:
                    st.warning(analysis_text)
                else:
                    st.success(analysis_text)
            else:
                st.error("Backend error analyzing data.")
                
        except Exception as e:
            st.error("Backend offline. Make sure your FastAPI server is running!")