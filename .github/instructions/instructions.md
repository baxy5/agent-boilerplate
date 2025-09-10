# Agent Playground - LangChain Boilerplate

This is a FastAPI-based boilerplate project for building LangChain agents with LangGraph. It provides a foundation for creating conversational AI agents with persistent chat history using PostgreSQL as the checkpoint storage.

## 🏗️ Project Architecture

### Core Components

- **FastAPI Server**: RESTful API server with CORS middleware
- **LangGraph**: State management for conversation flows
- **LangChain + OpenAI**: LLM integration for chat functionality
- **PostgreSQL**: Persistent storage for conversation checkpoints
- **Poetry**: Dependency management and virtual environment

### Project Structure

```
agent-playground/
├── app/
│   ├── main.py                 # FastAPI application setup
│   ├── server.py              # Server entry point
│   ├── api/
│   │   └── endpoints/
│   │       └── graph_example_route.py  # API routes
│   ├── services/
│   │   ├── env_config_service.py       # Environment configuration
│   │   └── graph_example_service.py    # Business logic
│   └── examples/
│       ├── graph_example.py           # Main LangGraph implementation
│       └── streaming_example.py       # Simple streaming example
├── pyproject.toml             # Poetry configuration
└── .env.example              # Environment variables template
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Poetry (Python dependency manager)
- PostgreSQL database
- OpenAI API key

### Installation

1. **Clone the repository** (if not already done):

   ```bash
   git clone <repository-url>
   cd agent-playground
   ```

2. **Install dependencies**:

   ```bash
   poetry install
   ```

3. **Set up environment variables**:

   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Fill in the required values:
     ```bash
     OPENAI_API_KEY=your_openai_api_key_here
     PSQL_USERNAME=your_postgres_username
     PSQL_PASSWORD=your_postgres_password
     PSQL_HOST=localhost
     PSQL_PORT=5432
     PSQL_DATABASE=your_database_name
     PSQL_SSLMODE=disable
     ```

4. **Set up PostgreSQL database**:
   - Create a PostgreSQL database
   - The application will automatically create the required `langgraph` schema on startup

### Running the Application

1. **Start the server**:

   ```bash
   poetry run start
   ```

   The server will start on `http://localhost:8000` with hot reload enabled.

2. **Access the API**:
   - Health check: `GET http://localhost:8000/`
   - Interactive docs: `http://localhost:8000/docs`
   - Chat endpoint: `POST http://localhost:8000/example/`

## 📡 API Usage

### Chat Endpoint

**POST** `/example/`

**Request Body**:

```json
{
  "input": "Hello, how are you?",
  "thread_id": "user123_conversation1"
}
```

**Response**:

```json
"I'm doing well, thank you for asking! How can I help you today?"
```

**Parameters**:

- `input` (string): The user's message/question
- `thread_id` (string): Unique identifier for the conversation thread (enables chat history persistence)

### Example Usage

```bash
curl -X POST "http://localhost:8000/example/" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What is the capital of France?",
    "thread_id": "conversation_123"
  }'
```

## 🧩 Key Features

### 1. Persistent Conversations

- Each conversation is identified by a `thread_id`
- Chat history is automatically stored in PostgreSQL
- Conversations can be resumed across sessions

### 2. Stateful Agent Architecture

The `ExampleGraph` class implements a stateful agent with:

- **AgentState**: Manages input, output, and chat history
- **LangGraph StateGraph**: Handles conversation flow
- **Checkpoint Saver**: Persists state between interactions

### 3. Environment Configuration

- Type-safe configuration using Pydantic
- Secure secret handling with `SecretStr`
- Automatic .env file loading

### 4. Error Handling

- Comprehensive exception handling at service and route levels
- Detailed error messages for debugging
- HTTP status codes for different error types

## 🛠️ Development

### Running Examples

1. **Interactive Graph Example**:

   ```bash
   poetry run python app/examples/graph_example.py
   ```

   This starts a command-line interface for testing the agent.

2. **Simple Streaming Example**:
   ```bash
   poetry run python app/examples/streaming_example.py
   ```
   Demonstrates basic LLM streaming without state management.

### Code Quality

The project uses Ruff for code formatting and linting:

```bash
# Format code
poetry run ruff format

# Check for issues
poetry run ruff check
```

**Ruff Configuration**:

- Line length: 100 characters
- Indent width: 2 spaces
- Import sorting enabled
- Excludes: `.git`, `__pycache__`, `.venv`

### Adding New Features

1. **New Endpoints**: Add routes in `app/api/endpoints/`
2. **Business Logic**: Create services in `app/services/`
3. **Agent Logic**: Implement graphs in `app/examples/` or create new modules
4. **Configuration**: Extend `EnvConfigService` for new environment variables

## 🔧 Configuration Details

### Environment Variables

| Variable         | Description                   | Required | Default |
| ---------------- | ----------------------------- | -------- | ------- |
| `OPENAI_API_KEY` | OpenAI API key for LLM access | Yes      | -       |
| `PSQL_USERNAME`  | PostgreSQL username           | Yes      | -       |
| `PSQL_PASSWORD`  | PostgreSQL password           | Yes      | -       |
| `PSQL_HOST`      | PostgreSQL host               | Yes      | -       |
| `PSQL_PORT`      | PostgreSQL port               | No       | 5432    |
| `PSQL_DATABASE`  | PostgreSQL database name      | Yes      | -       |
| `PSQL_SSLMODE`   | SSL mode for PostgreSQL       | No       | disable |

### CORS Configuration

The application allows CORS for:

- `http://localhost:3000` (React development server)
- `http://localhost:4200` (Angular development server)

Modify the `origins` list in `app/main.py` to add more allowed origins.

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**:

   - Ensure PostgreSQL is running
   - Verify database credentials in `.env`
   - Check if the database exists

2. **OpenAI API Error**:

   - Verify your OpenAI API key is valid
   - Check your OpenAI account has sufficient credits

3. **Import Errors**:

   - Ensure you're running commands with `poetry run`
   - Try `poetry install` to reinstall dependencies

4. **Port Already in Use**:
   - Change the port in `app/server.py` if 8000 is occupied
   - Or kill the process using port 8000

### Debug Mode

The server runs with `reload=True` for development. For production:

- Set `reload=False` in `app/server.py`
- Consider using a production ASGI server like Gunicorn

## 📚 Dependencies

### Core Dependencies

- **FastAPI**: Modern web framework for building APIs
- **LangChain**: Framework for developing LLM applications
- **LangGraph**: Library for building stateful agents
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type hints
- **psycopg**: PostgreSQL adapter for Python

### Development Dependencies

- **Ruff**: Fast Python linter and formatter

## 🎯 Next Steps

This boilerplate provides a solid foundation. Consider these enhancements:

1. **Authentication**: Add user authentication and authorization
2. **Rate Limiting**: Implement request rate limiting
3. **Monitoring**: Add logging and metrics collection
4. **Testing**: Create unit and integration tests
5. **Deployment**: Set up Docker containers and deployment scripts
6. **Multiple Agents**: Support different agent types and models
7. **Streaming Responses**: Implement streaming chat responses
8. **File Uploads**: Add support for document processing

## 📝 License

This project is a boilerplate template - customize the license as needed for your use case.
