# flask_api.py

from flask import Flask, jsonify, Response
from flask_cors import CORS  # Import CORS
import pandas as pd
from kafka import KafkaConsumer
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the cleaned dataset
df = pd.read_csv('cleaned_weather_data.csv')

@app.route('/data', methods=['GET'])
def get_data():
    """Endpoint to get the cleaned weather dataset."""
    return jsonify(df.to_dict(orient="records"))

@app.route('/stream', methods=['GET'])
def stream_weather_data():
    """Endpoint to stream live weather data from Kafka."""
    consumer = KafkaConsumer(
        'global_weather',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='weather_group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    def generate():
        try:
            for message in consumer:
                yield f"data:{json.dumps(message.value)}\n\n"
        except Exception as e:
            yield f"data:{{'error': '{str(e)}'}}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, port=5001)
