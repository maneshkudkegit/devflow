# DevFlow – DevOps Automation Hub 🚀

A production-ready full-stack platform for triggering DevOps operations from **Slack** or a sleek **web dashboard**. Manage GitHub workflows, Snowflake users, AWS services, and monitor all activity in real time.

![DevFlow](https://img.shields.io/badge/DevFlow-Automation%20Hub-6366f1?style=for-the-badge&logo=rocket&logoColor=white)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Dashboard** | Real-time stats, recent activity, and the CommandBox |
| **CommandBox** | Terminal-style input — type `deploy backend` just like Slack |
| **Deployments** | Trigger GitHub Actions workflows with one click |
| **User Management** | Create Snowflake users, assign roles, reset passwords |
| **AWS Integration** | Invoke Lambda functions, manage EC2 instances |
| **Slack Integration** | `/devflow` slash command routes to all services |
| **Activity Logs** | Complete audit trail stored in PostgreSQL / SQLite |

---

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────────┐     ┌─────────────┐
│   Slack Bot  │────▶│   FastAPI Backend   │◀────│  React UI   │
└──────────────┘     │                    │     └─────────────┘
                     │  ├─ GitHub Service │
                     │  ├─ Snowflake Svc  │
                     │  ├─ AWS Service    │
                     │  └─ Command Parser │
                     │                    │
                     │  ┌──────────────┐  │
                     │  │  PostgreSQL   │  │
                     │  │  (or SQLite)  │  │
                     │  └──────────────┘  │
                     └────────────────────┘
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone & start everything
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Local Development

#### Backend

```bash
cd backend

# Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy & configure environment
cp .env.example .env
# Edit .env with your credentials

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🔐 Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection string |
| `SLACK_BOT_TOKEN` | Slack bot OAuth token |
| `SLACK_SIGNING_SECRET` | Slack app signing secret |
| `GITHUB_TOKEN` | GitHub personal access token |
| `GITHUB_OWNER` | GitHub org/user |
| `GITHUB_REPO` | Repository name |
| `GITHUB_WORKFLOW_ID` | Workflow file name (e.g. `deploy.yml`) |
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier |
| `SNOWFLAKE_USER` | Snowflake admin username |
| `SNOWFLAKE_PASSWORD` | Snowflake admin password |
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_REGION` | AWS region |
| `AWS_LAMBDA_FUNCTION` | Lambda function name |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend URL (default: `http://localhost:8000`) |

> **Note:** When credentials are not configured, services return **mock responses** so you can explore the full UI without external accounts.

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/command` | Execute a free-text command |
| `POST` | `/api/deploy` | Trigger deployment |
| `GET` | `/api/logs` | Fetch activity logs |
| `GET` | `/api/stats` | Dashboard statistics |
| `POST` | `/api/users` | Create Snowflake user |
| `GET` | `/api/users` | List users |
| `POST` | `/api/users/reset` | Reset user password |
| `POST` | `/api/aws/lambda` | Invoke Lambda function |
| `GET` | `/api/aws/ec2` | List EC2 instances |
| `POST` | `/slack/commands` | Slack slash command endpoint |

---

## 🧪 CommandBox Examples

```
deploy backend
deploy frontend main
create_user john analyst
reset_password john
list_users
invoke_lambda my-function
list_ec2
start_ec2 i-0abc1234
```

---

## 📁 Project Structure

```
devflow/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py        # Environment configuration
│   │   │   └── database.py      # SQLAlchemy setup
│   │   ├── models/
│   │   │   └── logs.py          # Log ORM model
│   │   ├── routes/
│   │   │   ├── api.py           # REST API routes
│   │   │   └── slack.py         # Slack integration
│   │   ├── services/
│   │   │   ├── github_service.py
│   │   │   ├── snowflake_service.py
│   │   │   └── aws_service.py
│   │   └── utils/
│   │       └── parser.py        # Command parser
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── CommandBox.tsx
│   │   │   └── LogsTable.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Deployments.tsx
│   │   │   ├── Users.tsx
│   │   │   └── LogsPage.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🛡️ Tech Stack

**Backend:** FastAPI · SQLAlchemy · PostgreSQL/SQLite · boto3 · slack_sdk · snowflake-connector  
**Frontend:** React 18 · TypeScript · Vite · Tailwind CSS · React Query · Lucide Icons  
**Infra:** Docker · Nginx · PostgreSQL

---

## 📜 License

MIT
