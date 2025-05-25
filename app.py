from flask import Flask, request, jsonify, render_template, session, Response
from flask_cors import CORS
import os
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv
from agent import AgentFactory
from provider import ProviderFactory
import time

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
CORS(app)

# Persistent storage files
API_KEYS_FILE = 'api_keys.json'
CHAT_SESSIONS_FILE = 'chat_sessions.json'

# In-memory storage for API keys and chat sessions
api_keys = {}
chat_sessions = {}
agents = {}  # Store agent instances per session

def load_api_keys():
    """Load API keys from persistent storage"""
    global api_keys
    try:
        if os.path.exists(API_KEYS_FILE):
            with open(API_KEYS_FILE, 'r') as f:
                api_keys = json.load(f)
                print(f"Loaded {len(api_keys)} API key configurations from storage")
    except Exception as e:
        print(f"Error loading API keys: {e}")
        api_keys = {}

def save_api_keys():
    """Save API keys to persistent storage"""
    try:
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(api_keys, f, indent=2)
        print("API keys saved to storage")
    except Exception as e:
        print(f"Error saving API keys: {e}")

def load_chat_sessions():
    """Load chat sessions from persistent storage"""
    global chat_sessions
    try:
        if os.path.exists(CHAT_SESSIONS_FILE):
            with open(CHAT_SESSIONS_FILE, 'r') as f:
                chat_sessions = json.load(f)
                print(f"Loaded {len(chat_sessions)} chat sessions from storage")
    except Exception as e:
        print(f"Error loading chat sessions: {e}")
        chat_sessions = {}

def save_chat_sessions():
    """Save chat sessions to persistent storage"""
    try:
        with open(CHAT_SESSIONS_FILE, 'w') as f:
            json.dump(chat_sessions, f, indent=2)
    except Exception as e:
        print(f"Error saving chat sessions: {e}")

# Load data on startup
load_api_keys()
load_chat_sessions()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/keys', methods=['GET', 'POST', 'DELETE'])
def manage_api_keys():
    """Manage API keys for different providers"""
    if request.method == 'GET':
        # Return list of configured providers (without exposing keys)
        providers = {}
        for provider, key_info in api_keys.items():
            providers[provider] = {
                'configured': True,
                'models': key_info.get('models', [])
            }
        return jsonify(providers)
    
    elif request.method == 'POST':
        data = request.get_json()
        provider = data.get('provider')
        api_key = data.get('api_key')
        models = data.get('models', [])
        
        if not provider or not api_key:
            return jsonify({'error': 'Provider and API key are required'}), 400
        
        # Validate at least one model is provided
        if not models:
            return jsonify({'error': 'At least one model must be specified'}), 400
        
        # Test the API key with the first model
        try:
            test_provider = ProviderFactory.create_provider(provider, api_key, models[0])
            if not test_provider.validate_model():
                return jsonify({'error': f'Model "{models[0]}" not found for provider "{provider}". Please check the model name.'}), 400
        except Exception as e:
            return jsonify({'error': f'Failed to validate API key: {str(e)}'}), 400
        
        # Store API key with associated models
        api_keys[provider] = {
            'key': api_key,
            'models': models,
            'created_at': datetime.now().isoformat()
        }
        
        save_api_keys()  # Save to persistent storage
        
        return jsonify({'message': f'API key for {provider} saved successfully'})
    
    elif request.method == 'DELETE':
        provider = request.args.get('provider')
        if provider in api_keys:
            del api_keys[provider]
            save_api_keys()  # Save changes to persistent storage
            return jsonify({'message': f'API key for {provider} deleted'})
        return jsonify({'error': 'Provider not found'}), 404

@app.route('/api/chat/new', methods=['POST'])
def new_chat():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = {
        'id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'title': 'New Chat'
    }
    save_chat_sessions()  # Save to persistent storage
    return jsonify({'session_id': session_id})

@app.route('/api/chat/<session_id>/messages', methods=['GET', 'POST'])
def chat_messages(session_id):
    """Get or send messages in a chat session"""
    if session_id not in chat_sessions:
        return jsonify({'error': 'Chat session not found'}), 404
    
    if request.method == 'GET':
        return jsonify(chat_sessions[session_id]['messages'])
    
    elif request.method == 'POST':
        data = request.get_json()
        message = data.get('message')
        model_provider = data.get('model_provider')
        model_name = data.get('model_name')
        
        if not message or not model_provider or not model_name:
            return jsonify({'error': 'Message, model_provider, and model_name are required'}), 400
        
        # Check if API key exists for the provider
        if model_provider not in api_keys:
            return jsonify({'error': f'No API key configured for {model_provider}'}), 400
        
        # Check if model is in the configured models list
        if model_name not in api_keys[model_provider]['models']:
            return jsonify({'error': f'Model "{model_name}" not configured for provider "{model_provider}"'}), 400
        
        try:
            # Get or create agent for this session and model
            agent_key = f"{session_id}_{model_provider}_{model_name}"
            
            if agent_key not in agents:
                agents[agent_key] = AgentFactory.create_agent(
                    'chat',  # agent type
                    model_provider,
                    api_keys[model_provider]['key'],
                    model_name
                )
            
            agent = agents[agent_key]
            
            # Add user message to session
            user_message = {
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            }
            chat_sessions[session_id]['messages'].append(user_message)
            
            # Generate response using the agent
            response = agent.process_message(message)
            
            # Add assistant response to session
            assistant_message = {
                'role': 'assistant',
                'content': str(response),
                'timestamp': datetime.now().isoformat(),
                'model': f"{model_provider}/{model_name}"
            }
            chat_sessions[session_id]['messages'].append(assistant_message)
            
            # Update chat title if this is the first exchange
            if len(chat_sessions[session_id]['messages']) == 2:
                chat_sessions[session_id]['title'] = message[:50] + ('...' if len(message) > 50 else '')
            
            save_chat_sessions()  # Save changes to persistent storage
            
            return jsonify(assistant_message)
            
        except Exception as e:
            error_msg = f'Failed to generate response: {str(e)}'
            return jsonify({'error': error_msg}), 500

@app.route('/api/chat/<session_id>/stream', methods=['POST'])
def stream_chat_message(session_id):
    """Stream chat messages with letter-by-letter response"""
    if session_id not in chat_sessions:
        return jsonify({'error': 'Chat session not found'}), 404
    
    data = request.get_json()
    message = data.get('message')
    model_provider = data.get('model_provider')
    model_name = data.get('model_name')
    
    if not message or not model_provider or not model_name:
        return jsonify({'error': 'Message, model_provider, and model_name are required'}), 400
    
    # Check if API key exists for the provider
    if model_provider not in api_keys:
        return jsonify({'error': f'No API key configured for {model_provider}'}), 400
    
    # Check if model is in the configured models list
    if model_name not in api_keys[model_provider]['models']:
        return jsonify({'error': f'Model "{model_name}" not configured for provider "{model_provider}"'}), 400
    
    def generate_stream():
        try:
            # Get or create agent for this session and model
            agent_key = f"{session_id}_{model_provider}_{model_name}"
            
            if agent_key not in agents:
                agents[agent_key] = AgentFactory.create_agent(
                    'chat',  # agent type
                    model_provider,
                    api_keys[model_provider]['key'],
                    model_name
                )
            
            agent = agents[agent_key]
            
            # Add user message to session
            user_message = {
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            }
            chat_sessions[session_id]['messages'].append(user_message)
            
            # Send user message event
            yield f"data: {json.dumps({'type': 'user_message', 'data': user_message})}\n\n"
            
            # Generate response using the agent
            response = agent.process_message(message)
            
            # Stream the response letter by letter
            assistant_message = {
                'role': 'assistant',
                'content': '',
                'timestamp': datetime.now().isoformat(),
                'model': f"{model_provider}/{model_name}"
            }
            
            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'data': assistant_message})}\n\n"
            
            # Stream each character with a small delay
            for char in str(response):
                assistant_message['content'] += char
                yield f"data: {json.dumps({'type': 'chunk', 'data': {'content': char, 'full_content': assistant_message['content']}})}\n\n"
                time.sleep(0.03)  # 30ms delay between characters
            
            # Add complete response to session
            chat_sessions[session_id]['messages'].append(assistant_message)
            
            # Update chat title if this is the first exchange
            if len(chat_sessions[session_id]['messages']) == 2:
                chat_sessions[session_id]['title'] = message[:50] + ('...' if len(message) > 50 else '')
            
            # Save changes to persistent storage
            save_chat_sessions()
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'complete', 'data': assistant_message})}\n\n"
            
        except Exception as e:
            error_msg = f'Failed to generate response: {str(e)}'
            yield f"data: {json.dumps({'type': 'error', 'data': {'error': error_msg}})}\n\n"
    
    return Response(generate_stream(), content_type='text/plain; charset=utf-8')

@app.route('/api/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get list of all chat sessions"""
    sessions = []
    for session in chat_sessions.values():
        sessions.append({
            'id': session['id'],
            'title': session['title'],
            'created_at': session['created_at'],
            'message_count': len(session['messages'])
        })
    return jsonify(sorted(sessions, key=lambda x: x['created_at'], reverse=True))

@app.route('/api/chat/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a chat session"""
    if session_id in chat_sessions:
        # Clean up associated agents
        keys_to_remove = [key for key in agents.keys() if key.startswith(session_id)]
        for key in keys_to_remove:
            del agents[key]
        
        del chat_sessions[session_id]
        save_chat_sessions()  # Save changes to persistent storage
        return jsonify({'message': 'Chat session deleted'})
    return jsonify({'error': 'Chat session not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)