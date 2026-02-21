<div align="center" style="text-align: center;">

<h1>Multi-Agent Orchestrator</h1>

<p>
  <b>An agent which Plans, schedules tasks and reviews your work with detailed Report.</b>
  <br>
</p>

<h3>
  <a href="">Docs</a>
</h3>

</div>

## Getting Started

### Software Requirements

- Python
- Nodejs
- npm
- poetry
- OpenRouter API Key

## Quick Setup

```
git clone https://github.com/Kiranpatil02/Multiagent-Orchestration.git
```

Install dependency packages
```
poetry install
```
Start the Worker
- This creates a light weight DB
- Initialises DB schemeas which helps agents claim tasks

```
poetry run python worker.py
```

Start the Backend API
- To talk between Frontend and Backend
- Backend would start listening on port http://127.0.0.1:8000 

```
poetry run python uvicorn api.api:app
```
Frontend setup

```
cd frontend/
```
Install dependencies:
- Installs React(Vite) and Tailwindcss
```
npm install
```
Start the Server
- The frontend would be up on http://localhost:5173

```
npm run dev
```








