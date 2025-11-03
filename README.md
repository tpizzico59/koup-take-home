# Kouper Care Coordinator Assistant

AI-powered healthcare scheduling assistant using ReAct pattern with OpenAI function calling. This intelligent care coordinator is assistant first, agent second; it allows for actual appointment scheduling as well as pure information retrieval.  

## Architecture

```
┌──────────────┐
│   Frontend   │  React + Vite (manages conversation state)
│   :3000      │
└──────┬───────┘
       │ POST /chat (sends full message history, the backend is stateless)
       ↓
┌──────────────┐
│   Backend    │  Flask API + OpenAI (stateless)
│   :5000      │  - Executes tool loop
└──┬───────┬───┘  - Returns final response
   │       │
   ↓       ↓
┌─────┐ ┌─────┐
│ DB  │ │ API │  PostgreSQL + Patient API
│:5432│ │:5001│
└─────┘ └─────┘
```

## Setup

### Prerequisites
- Python 3.11
- Node.js 18+
- PostgreSQL 14+
- OpenAI API key

### 1. Database Setup (Terminal 1)

```bash
# Create database
createdb care_coordinator

# Run schema and seed
psql care_coordinator < database/schema.sql
psql care_coordinator < database/seed.sql
```

### 2. Backend Setup (Terminal 2)

```bash
cd backend

# Install dependencies
python3.11 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
# Copy contents of .env.example into a .env file at the root of the repo 
# Edit .env: Add OPENAI_API_KEY and DATABASE_URL. 
# **NOTE: On mac, user is probably the output of whoami command if postgres user not set. 

# Run backend
python3.11 app.py
```

### 3. Patient API Setup (Terminal 3)

```bash
cd api
# Install dependencies
python3.11 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt

# Run patient API (simulates external service)
python3.11 patient_api.py
```

### 4. Frontend Setup (Terminal 4)

```bash
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

## Usage

1. Open http://localhost:3000
2. Chat with the assistant to schedule appointments
3. Frontend sends full conversation history on each message
4. Backend uses ReAct loop to execute tools and respond

## Key Features

- **Stateless Backend**: No session storage, frontend manages state
- **ReAct Pattern**: LLM decides which tools to call based on system prompt
- **Tool Execution**: Automatic function calling loop until completion
- **Database-First**: All provider and appointment data in PostgreSQL