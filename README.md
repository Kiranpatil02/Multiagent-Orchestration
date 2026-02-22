<div align="center" style="text-align: center;">

<h1>Multi-Agent Orchestrator</h1>

<p>
  <b>An agent which Plans, schedules tasks and reviews your work with detailed Report.</b>
  <br>
</p>

<h3>
  <a href="https://docs.google.com/document/d/1EjuRAqx93Ntkm3Loq78OnGxXs1kYUnDE/edit?usp=drive_link&ouid=104595812794159257675&rtpof=true&sd=true">Docs</a>
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
### Backend

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
### Frontend

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

## Agents Workflow

### 1. Planner Agent
- Breaks the user’s request into discrete sub-tasks and determines
execution order.

### 2. Research Agent
- Gathers information for each sub-task

### 3. Writer Agent
- Synthesizes research into a draft report.

### 4. Reviewer Agent
- Evaluates the draft, provides feedback, and can send it back for
revision.









