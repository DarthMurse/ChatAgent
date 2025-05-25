# Chat Agent

A web-based chat agent interface that supports multiple LLM providers (OpenAI, Claude, DeepSeek) using the smolagents library.

## Features

- **Multi-Provider Support**: Configure API keys for OpenAI, Claude (Anthropic), and DeepSeek
- **Web GUI Interface**: Clean, modern web interface for chatting
- **Multi-Turn Conversations**: Support for ongoing conversations with context
- **Session Management**: Create new chats and manage multiple chat sessions
- **Model Selection**: Choose between different models from configured providers
- **API Key Management**: Securely manage API keys through the web interface

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Copy the `.env` file and update with your preferred settings:

```bash
cp .env .env.local
```

Edit `.env.local` to set your secret key and optionally default API keys.

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### 1. Configure API Keys

1. Open the web interface at `http://localhost:5000`
2. In the sidebar, use the "API Keys" section to add your credentials:
   - Select a provider (OpenAI, Claude, or DeepSeek)
   - Enter your API key
   - Specify available models (comma-separated)
   - Click "Save Key"

**Example model configurations:**
- **OpenAI**: `gpt-4,gpt-3.5-turbo,gpt-4-turbo`
- **Claude**: `claude-3-opus-20240229,claude-3-sonnet-20240229,claude-3-haiku-20240307`
- **DeepSeek**: `deepseek-chat,deepseek-coder`

### 2. Start Chatting

1. Click "New Chat" to create a new conversation
2. Select a model from the dropdown in the header
3. Type your message and press Enter or click Send
4. The agent will respond using smolagents with your chosen model

### 3. Manage Sessions

- **View Sessions**: All chat sessions appear in the sidebar
- **Switch Sessions**: Click on any session to load it
- **Session Titles**: Automatically generated from the first message
- **Persistent Storage**: Sessions are stored in memory (restart to clear)

## API Endpoints

The application provides a REST API:

- `GET /api/keys` - List configured providers
- `POST /api/keys` - Add/update API key
- `DELETE /api/keys?provider=<name>` - Remove API key
- `POST /api/chat/new` - Create new chat session
- `GET /api/chat/sessions` - List all sessions
- `GET /api/chat/<id>/messages` - Get session messages
- `POST /api/chat/<id>/messages` - Send message to session
- `DELETE /api/chat/<id>` - Delete session

## Architecture

- **Backend**: Flask web server with REST API
- **Frontend**: Vanilla JavaScript with modern CSS
- **Agent Library**: smolagents for LLM interactions
- **Storage**: In-memory (suitable for development/demos)

## Security Notes

- API keys are stored in memory only
- Use HTTPS in production
- Change the SECRET_KEY in production
- Consider using a proper database for persistent storage

## Supported Providers

### OpenAI
- Models: GPT-4, GPT-3.5-turbo, etc.
- Requires OpenAI API key

### Claude (Anthropic)
- Models: Claude-3 family (Opus, Sonnet, Haiku)
- Requires Anthropic API key

### DeepSeek
- Models: DeepSeek-Chat, DeepSeek-Coder
- Requires DeepSeek API key

## Development

To extend the application:

1. **Add new providers**: Update the `ChatAgent.get_or_create_agent()` method
2. **Add tools**: Modify the `CodeAgent(tools=[])` initialization
3. **Persistent storage**: Replace in-memory storage with a database
4. **Authentication**: Add user authentication and session management

## Troubleshooting

**Common Issues:**

1. **"No API key configured"**: Ensure you've added API keys through the web interface
2. **Model not available**: Check that the model name matches your provider's available models
3. **Connection errors**: Verify your API keys are valid and have sufficient credits
4. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

**Dependencies:**
- smolagents: Core agent functionality
- flask: Web framework
- flask-cors: Cross-origin resource sharing
- openai: OpenAI API client
- anthropic: Anthropic API client
- requests: HTTP requests
- python-dotenv: Environment variable loading