import os
from flask import Flask, request, jsonify, render_template
import openai
from flask_cors import CORS
from dotenv import load_dotenv
from youtube_transcript_api import *

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
CORS(app)  # Allow all origins

@app.route('/')
def home():
    return render_template("index.html")

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text, None
    except Exception as e:
        return None, str(e)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    video_url = data.get('url')
    video_id = video_url.split("v=")[-1]

    transcript_text, error = get_transcript(video_id)
    if error:
        return jsonify({'error': 'Could not fetch transcript: ' + error}), 500

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text:\n\n{transcript_text}"}
            ],
            max_tokens=2048,
            temperature=0.7,
        )
        summary = response.choices[0].message['content'].strip()
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
