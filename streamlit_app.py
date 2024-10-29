# streamlit_app.py

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objs as go
import json
import time

st.title("Global Weather Dashboard")
API_BASE_URL = "https://flask-mj1k.onrender.com"
# API_BASE_URL = "http://localhost:5001"

@st.cache_data
def load_data():
    response = requests.get(f"{API_BASE_URL}/data")
    print("Status Code:", response.status_code)  # Should be 200
    print("Response Text:", response.text)        # Check the raw response content
    data = response.json()
    return pd.DataFrame(data)

data = load_data()

st.header("Data Dashboard")
selected_region = st.selectbox("Select Region", options=data['location_name'].unique())
filtered_data = data[data['location_name'] == selected_region]
st.write(filtered_data)
fig = px.scatter(filtered_data, x="temperature_celsius", y="humidity", color="location_name",
                 title=f"Temperature and Humidity for {selected_region}")
st.plotly_chart(fig)

st.header("Live Data Updates")
placeholder = st.empty()
fig = go.Figure()

stream_url = f"{API_BASE_URL}/stream"
with requests.get(stream_url, stream=True) as response:
    for line in response.iter_lines():
        if line:
            weather_data = json.loads(line.decode('utf-8').split("data:")[1])
            fig.add_trace(go.Scatter(x=[weather_data['temperature_celsius']], y=[weather_data['humidity']], mode='markers'))
            fig.update_layout(title="Real-Time Weather Updates", xaxis_title="Temperature (°C)", yaxis_title="Humidity (%)")
            placeholder.plotly_chart(fig)
            time.sleep(1)
