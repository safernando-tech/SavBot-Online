# Import necessary modules from Flask
from flask import Flask, request, jsonify
# CORS is needed to allow your HTML/JS to talk to this Python server
from flask_cors import CORS
import time
import requests # We need this to make HTTP requests to the AI API
import os # New import for environment variables

# Create a Flask web application instance
app = Flask(__name__)
# Enable CORS for all routes, allowing requests from your frontend HTML
CORS(app)

# Your API Key for the powerful AI model.
# PASTE YOUR REAL API KEY HERE, BETWEEN THE QUOTES!
# Example: API_KEY = "YOUR_SUPER_SECRET_API_KEY_GOES_HERE"
API_KEY = "" # Replace "" with your actual API key.

# URL for the Gemini API (using a specific version suitable for text generation)
GEMINI_TEXT_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"

# This function will now try to get a response from a powerful AI model (for text)
async def get_ai_response_from_api(chat_history):
    payload = {
        "contents": chat_history
    }

    headers = {
        "Content-Type": "application/json"
    }

    retries = 3
    delay = 1
    for i in range(retries):
        try:
            response = requests.post(GEMINI_TEXT_API_URL, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            if result.get('candidates') and result['candidates'][0].get('content') and \
               result['candidates'][0]['content'].get('parts') and \
               result['candidates'][0]['content']['parts'][0].get('text'):
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Unexpected text API response structure: {result}")
                return "I couldn't get a clear answer from the AI. Maybe try rephrasing?"
        except requests.exceptions.RequestException as e:
            print(f"Text API request failed (attempt {i+1}/{retries}): {e}")
            if i < retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return f"Sorry, I couldn't reach the AI for text at the moment. (Error: {e})"
        except Exception as e:
            print(f"An unexpected error occurred during text generation: {e}")
            return "An unexpected error occurred while processing your text request."
    return "Something went wrong and I couldn't get a text response."

# New: Define a root route for the main URL
@app.route('/', methods=['GET'])
def home():
    return "SavBot Backend is running! Access the chat interface via your index.html file."

# Define a route for handling text responses
@app.route('/generate-response', methods=['POST'])
async def handle_generate_response():
    data = request.get_json()
    chat_history = data.get('chat_history', [])

    if not chat_history:
        return jsonify({'response': "Savbot: Please provide a question for me to answer."})

    user_prompt = chat_history[-1]['parts'][0]['text'].lower().strip()

    # --- DEBUGGING PRINT ---
    print(f"Received user_prompt: '{user_prompt}'")
    # --- END DEBUGGING PRINT ---

    response_text = ""

    # --- Implement Specific Answers & Basic Topic/Mood Recognition ---
    if user_prompt == "what's your name":
        response_text = "My name is Savbot."
    elif user_prompt == "who made you":
        response_text = "I was made by Savitha .F and Gemini."
    elif "joke" in user_prompt or user_prompt == "tell me a joke":
        response_text = "Why don't scientists trust atoms? Because they make up everything! 😂"
    elif "fun fact" in user_prompt or user_prompt == "give me a fun fact":
        response_text = "Did you know that a group of owls is called a parliament? 🦉"
    elif "happy" in user_prompt or "great" in user_prompt or "good mood" in user_prompt:
        response_text = "That's wonderful to hear! I'm glad you're feeling good! 😊"
    elif "sad" in user_prompt or "down" in user_prompt or "bad mood" in user_prompt:
        response_text = "I'm sorry to hear that. Is there anything I can do to help cheer you up? 🫂"
    else:
        # If no local command/mood matches, send the full chat history to the powerful AI model
        ai_response = await get_ai_response_from_api(chat_history)
        response_text = ai_response

    # Add the "Savbot: " prefix to the final response
    final_response = f"Savbot: {response_text}"
    return jsonify({'response': final_response})

# Run the Flask application
if __name__ == '__main__':
    # Render (and other hosting platforms) will provide a PORT environment variable.
    # We need to tell Flask to listen on that port and on all available network interfaces (0.0.0.0).
    port = int(os.environ.get("PORT", 5000)) # Get port from environment, or use 5000 as default
    print(f"SavBot Backend Server running on http://0.0.0.0:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True)
