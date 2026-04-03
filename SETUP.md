# Setup Instructions for EduAI Platform

## Complete Installation Guide

This guide will walk you through setting up the entire EduAI platform from scratch.

## Step 1: System Preparation

### Required Downloads
1. **Python 3.10+**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Node.js 18+**
   - Download from [nodejs.org](https://nodejs.org/)
   - Includes npm automatically

3. **Ollama**
   - Download from [ollama.ai](https://ollama.ai)
   - Used for running LLMs locally

4. **MongoDB Community Server** (Optional - can use MongoDB Atlas)
   - Download from [mongodb.com](https://www.mongodb.com/try/download/community)
   - Or use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (cloud)

### Verify Installation
```bash
# Check Python
python --version

# Check Node.js and npm
node --version
npm --version

# Check Ollama
ollama --version
```

---

## Step 2: Backend Setup

### 2.1 Navigate to Backend Directory
```bash
cd "x:\Final year project\backend"
```

### 2.2 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 2.3 Install Python Packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configure Environment Variables
```bash
# Copy the template
cp .env.example .env

# Edit .env file with your settings
# For Windows, use Notepad or VS Code
```

**Important .env configurations:**
```env
# Server
FLASK_ENV=development
FLASK_APP=run.py
FLASK_PORT=5000

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-change-in-production-12345678
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production-87654321
JWT_ALGORITHM=HS256

# MongoDB
# Option 1: Local
MONGODB_URI=mongodb://localhost:27017/educational_platform

# Option 2: MongoDB Atlas (Recommended)
# Create account at https://www.mongodb.com/cloud/atlas
# Get connection string from cluster settings
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/educational_platform

MONGODB_DB_NAME=educational_platform

# AI Model
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# File Upload
MAX_CONTENT_LENGTH=52428800
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=pdf,docx,txt,doc

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5000

# Logging
LOG_LEVEL=INFO
```

### 2.5 Setup MongoDB

**Option A: Local MongoDB**
```bash
# Start MongoDB service (Windows)
net start MongoDB

# Or manually start mongod.exe from installation folder
```

**Option B: MongoDB Atlas (Recommended)**
1. Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Sign up (free tier available)
3. Create a cluster
4. Get connection string
5. Update `MONGODB_URI` in `.env`
6. Add your IP to network access list

### 2.6 Setup Ollama

```bash
# Start Ollama service (in another terminal/command prompt)
ollama serve

# In a new terminal, pull a model
ollama pull mistral

# Other available models:
ollama pull llama2              # Good general model
ollama pull neural-chat         # Optimized for chat
ollama pull dolphin-mixtral     # Advanced model

# Verify model loaded
ollama list
```

### 2.7 Test Backend
```bash
# In backend directory with venv activated
python run.py

# Should see:
# * Running on http://127.0.0.1:5000
# * Database connected successfully
```

Visit `http://localhost:5000/health` - should return:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Step 3: Frontend Setup

### 3.1 Navigate to Frontend Directory
```bash
cd ../frontend
```

### 3.2 Install Dependencies
```bash
npm install

# If installation is slow, try:
npm install --legacy-peer-deps
```

### 3.3 Configure Environment
```bash
# Copy the template
cp .env.example .env
```

**Edit `.env`:**
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENVIRONMENT=development
REACT_APP_AI_MODEL=mistral
```

### 3.4 Start Development Server
```bash
npm run dev

# Should output:
# VITE v5.0.0 ready in 123 ms
# ➜ Local: http://localhost:3000
```

---

## Step 4: Testing the Platform

### 4.1 Access the Application
1. Open browser
2. Go to `http://localhost:3000`
3. You should see the login page

### 4.2 Test Account Creation
1. Click "Sign up"
2. Create account:
   - Email: `student@example.com`
   - Password: `Test12345`
   - Name: `John Student`
   - Role: `Student`
   - Institution: `Test University`
3. Click "Sign Up"
4. You should be redirected to Dashboard

### 4.3 Test Chat Feature
1. Click "Chat" in navigation
2. Click "New Chat"
3. Ask a question: "What is photosynthesis?"
4. Should get a response from Ollama

### 4.4 Test Teacher Features
1. Sign up as Teacher
2. Go to "Notes"
3. Create a sample PDF or text file
4. Click "Upload Note"
5. Fill in details and upload
6. Note should appear in the list

---

## Step 5: Database Initialization

The database will auto-initialize when the backend starts. To manually create indexes:

```bash
# In backend directory with venv activated
python

# In Python console:
from app.db import db
db.connect()
db._create_indexes()
exit()
```

---

## Useful Terminal Commands

### Backend Management
```bash
# Stop backend (Ctrl+C in terminal)

# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process using port
taskkill /PID <PID_NUMBER> /F
```

### Frontend Management
```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Clean cache
npm cache clean --force
```

### Database Backup
```bash
# Backup local MongoDB
mongodump --db educational_platform --out D:\backups

# Restore
mongorestore --db educational_platform D:\backups\educational_platform
```

---

## Troubleshooting

### Backend Won't Start

**Error: "Address already in use"**
```bash
# Kill process on port 5000
taskkill /PID <PID> /F

# Or change port in config.py
```

**Error: "MongoDB connection failed"**
```bash
# Check if MongoDB is running
# Windows: Services > MongoDB
# Mac: brew services list | grep mongodb
# Linux: sudo systemctl status mongod

# Or check connection string in .env
```

**Error: "Ollama not responding"**
```bash
# Make sure Ollama is running
ollama serve

# Check if model is pulled
ollama list

# If missing, pull it
ollama pull mistral
```

### Frontend Won't Start

**Error: "Port 3000 already in use"**
```bash
# Kill process or change port in vite.config.js
```

**Error: "npm install fails"**
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules
npm install
```

### Connection Issues

**Frontend can't reach backend**
- Check backend is running on port 5000
- Verify `REACT_APP_API_URL` in frontend `.env`
- Check CORS_ORIGINS in backend `.env`
- Check browser console for errors (F12)

**API returns 401 Unauthorized**
- Log in first
- Check JWT token is stored in localStorage
- Sign up and log in again

---

## Environment Setup Checklist

- [ ] Python installed and in PATH
- [ ] Node.js and npm installed
- [ ] Virtual environment created and activated
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] MongoDB running (local or Atlas)
- [ ] Ollama running with model pulled
- [ ] Backend `.env` configured
- [ ] Frontend `.env` configured
- [ ] Backend running on port 5000
- [ ] Frontend running on port 3000
- [ ] Can access `http://localhost:3000`
- [ ] Can sign up and log in
- [ ] Chat responds to questions
- [ ] Can upload notes (as teacher)

---

## Next Steps

1. **Explore the Dashboard**: Familiarize yourself with the interface
2. **Read API Documentation**: Check the README for API endpoints
3. **Review Code**: Study the architecture in ARCHITECTURE.md
4. **Customize**: Modify themes, colors, and features
5. **Deploy**: Follow deployment guide in README.md

---

## Getting Help

1. Check browser console (F12) for error messages
2. Check terminal output for backend errors
3. Review troubleshooting section
4. Check project documentation
5. Create an issue with details

---

**Setup Estimated Time**: 30-45 minutes

Good luck! 🚀
