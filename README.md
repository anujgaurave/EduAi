# EduAI - AI-Powered Educational Platform

A comprehensive, full-stack educational platform that leverages artificial intelligence to provide personalized learning experiences. Built with React.js, Python Flask, MongoDB, and open-source LLMs.

## 🎯 Features

### Core Features
- **AI Chat Assistant**: ChatGPT-like interface for syllabus-based Q&A
- **Retrieval-Augmented Generation (RAG)**: Context-aware responses using learning materials
- **Role-Based Access**: Separate interfaces for students and teachers
- **JWT Authentication**: Secure login and session management
- **File Processing**: Extract and process PDFs, DOCX, and TXT files

### Student Module
- Interactive AI chat with context awareness
- Ask questions about syllabus topics
- Get explanations, summaries, and examples
- Auto-generated quizzes and mock tests
- Track learning progress with analytics
- Access learning materials and notes
- Take assessments and view results

### Teacher Module
- Upload and manage learning materials
- Create and publish assessments
- Generate questions automatically with AI
- View student performance analytics
- Manage content and resources

### Technical Features
- Vector database with FAISS for embeddings
- Prompt injection prevention
- Caching for performance optimization
- Async processing for file uploads
- Dark/Light mode support
- Mobile-responsive design
- Comprehensive error handling

## 📋 Prerequisites

### Required Software
- Python 3.9+
- Node.js 16+ and npm
- MongoDB 4.4+ (or MongoDB Atlas)
- Ollama (for local LLM deployment)

### System Requirements
- 8GB+ RAM
- 10GB disk space
- Stable internet connection

## 🚀 Quick Start

### 1. Clone the Repository
```bash
cd "x:\Final year project"
```

### 2. Backend Setup

#### Create Python Virtual Environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Setup Environment Variables
```bash
# Copy and configure
cp .env.example .env
```

Then edit `.env` file:
```env
FLASK_ENV=development
MONGODB_URI=mongodb://localhost:27017/educational_platform
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/educational_platform
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

#### Install Ollama
Download from [ollama.ai](https://ollama.ai)

```bash
# Pull a model
ollama pull mistral
# Or try other models:
ollama pull llama2
ollama pull neural-chat
```

#### Start Ollama (in separate terminal)
```bash
ollama serve
```

#### Run Backend
```bash
python run.py
```

Backend will be available at: `http://localhost:5000`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd ../frontend
npm install
```

#### Setup Environment Variables
```bash
cp .env.example .env
```

Edit `.env`:
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENVIRONMENT=development
```

#### Start Development Server
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 4. Access the Application
- Open browser: `http://localhost:3000`
- Sign up as Student or Teacher
- Start exploring!

## 📁 Project Structure

```
Final year project/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── config.py                # Configuration management
│   │   ├── db.py                    # MongoDB connection
│   │   ├── models/
│   │   │   ├── user.py              # User model
│   │   │   ├── chat.py              # Chat sessions
│   │   │   ├── note.py              # Learning materials
│   │   │   ├── assessment.py        # Quizzes & tests
│   │   │   └── progress.py          # Student progress
│   │   ├── routes/
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── chat.py              # Chat endpoints
│   │   │   ├── notes.py             # Notes management
│   │   │   ├── assessments.py       # Assessment endpoints
│   │   │   └── progress.py          # Progress tracking
│   │   ├── services/
│   │   │   └── ai_service.py        # AI/LLM integration
│   │   ├── utils/
│   │   │   ├── helpers.py           # Utility functions
│   │   │   ├── file_processor.py    # File extraction
│   │   │   └── vector_store.py      # Vector DB (FAISS)
│   │   └── middleware/              # Custom middleware
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Example environment variables
│   └── run.py                       # Application entry point
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── LoginPage.jsx
    │   │   ├── SignupPage.jsx
    │   │   ├── DashboardPage.jsx
    │   │   ├── ChatPage.jsx
    │   │   ├── NotesPage.jsx
    │   │   ├── AssessmentsPage.jsx
    │   │   ├── ProgressPage.jsx
    │   │   └── ProfilePage.jsx
    │   ├── components/
    │   │   ├── Navigation.jsx
    │   │   └── ProtectedRoute.jsx
    │   ├── services/
    │   │   └── api.js               # API client
    │   ├── store/
    │   │   └── index.js             # Zustand stores
    │   ├── styles/
    │   │   └── index.css            # Global styles
    │   ├── App.jsx                  # Main app component
    │   └── main.jsx                 # React entry point
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── index.html
    └── .env.example
```

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/signup              # User registration
POST   /api/auth/login               # User login
GET    /api/auth/profile             # Get user profile
PUT    /api/auth/profile             # Update profile
POST   /api/auth/change-password     # Change password
POST   /api/auth/deactivate          # Deactivate account
```

### Chat
```
GET    /api/chat/sessions            # Get user's chat sessions
POST   /api/chat/sessions            # Create new chat
GET    /api/chat/sessions/<id>       # Get chat details
POST   /api/chat/sessions/<id>/message # Send message
DELETE /api/chat/sessions/<id>       # Delete chat
PUT    /api/chat/sessions/<id>/title # Update chat title
GET    /api/chat/search              # Search chats
```

### Notes
```
GET    /api/notes                    # Get all notes (paginated)
POST   /api/notes/upload             # Upload note (teacher)
GET    /api/notes/<id>               # Get note details
GET    /api/notes/teacher/<id>       # Get teacher's notes
DELETE /api/notes/<id>               # Delete note (teacher)
GET    /api/notes/search             # Search notes
GET    /api/notes/rag-search         # RAG-based search
```

### Assessments
```
POST   /api/assessments/create       # Create assessment (teacher)
GET    /api/assessments/<id>         # Get assessment
POST   /api/assessments/publish/<id> # Publish assessment
POST   /api/assessments/submit/<id>  # Submit answers
POST   /api/assessments/generate-quiz # AI quiz generation
GET    /api/assessments/available    # Get available assessments
```

### Progress
```
GET    /api/progress/my-progress     # Get student progress
GET    /api/progress/student/<id>    # Get student progress (teacher)
GET    /api/progress/stats           # Get performance stats
POST   /api/progress/update-score    # Update score
GET    /api/progress/leaderboard     # Get leaderboard
```

## 🗄️ Database Schema

### Collections

#### users
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password_hash: String,
  name: String,
  role: 'student' | 'teacher',
  created_at: Date,
  updated_at: Date,
  is_active: Boolean,
  profile: {
    bio: String,
    avatar: String,
    phone: String,
    institution: String
  }
}
```

#### chats
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  title: String,
  messages: [{
    _id: ObjectId,
    role: 'user' | 'assistant',
    content: String,
    timestamp: Date,
    tokens_used: Number
  }],
  created_at: Date,
  updated_at: Date,
  is_deleted: Boolean
}
```

#### notes
```javascript
{
  _id: ObjectId,
  title: String,
  content: String,
  teacher_id: ObjectId,
  file_type: 'pdf' | 'docx' | 'txt',
  subject: String,
  topic: String,
  description: String,
  file_path: String,
  embeddings_stored: Boolean,
  created_at: Date,
  updated_at: Date,
  is_published: Boolean
}
```

#### assessments
```javascript
{
  _id: ObjectId,
  title: String,
  questions: [ObjectId],
  teacher_id: ObjectId,
  subject: String,
  total_marks: Number,
  duration_minutes: Number,
  passing_percentage: Number,
  created_at: Date,
  is_published: Boolean
}
```

#### questions
```javascript
{
  _id: ObjectId,
  question_text: String,
  question_type: 'mcq' | 'short_answer' | 'essay',
  options: [String],
  correct_answer: String,
  marks: Number,
  explanation: String,
  difficulty: 'easy' | 'medium' | 'hard'
}
```

#### progress
```javascript
{
  _id: ObjectId,
  student_id: ObjectId (unique),
  total_questions_answered: Number,
  correct_answers: Number,
  average_score: Number,
  assessments_taken: [{
    assessment_id: ObjectId,
    score: Number,
    date: Date
  }],
  learning_streak: Number,
  created_at: Date,
  updated_at: Date
}
```

## 🔒 Security Features

### Implemented Security Measures
1. **JWT Authentication**: Secure token-based auth
2. **Password Hashing**: bcrypt for secure password storage
3. **Input Validation**: Sanitization to prevent injection
4. **CORS Protection**: Configured allowed origins
5. **Rate Limiting**: Built-in rate limiter for APIs
6. **Role-Based Access Control**: Student/Teacher separation
7. **File Upload Security**: Type and size validation
8. **Prompt Injection Prevention**: Input checks before LLM calls

### Best Practices
- Never commit `.env` files
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Implement database backups
- Monitor for suspicious activities
- Keep dependencies updated

## 🚀 Deployment

### Backend Deployment (Render.com)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up and create new Web Service

2. **Connect GitHub Repository**
   - Link your GitHub repository
   - Select Python environment

3. **Configure Environment**
   ```
   FLASK_ENV=production
   MONGODB_URI=<your-mongodb-atlas-uri>
   SECRET_KEY=<generate-secure-key>
   JWT_SECRET_KEY=<generate-secure-key>
   ```

4. **Deploy**
   - Set start command: `python run.py`
   - Deploy!

### Frontend Deployment (Vercel)

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub project

2. **Configure Environment**
   - Add environment variable:
   ```
   REACT_APP_API_URL=<your-backend-url>
   ```

3. **Deploy**
   - Vercel automatically deploys on push

### Database (MongoDB Atlas)

1. **Create Cluster**
   - Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
   - Create free tier cluster

2. **Get Connection String**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/educational_platform
   ```

3. **Update Backend Config**
   - Set `MONGODB_URI` in production environment

## 📊 Performance Optimization

### Implemented Optimizations
- Vector DB caching with FAISS
- Query indexing on MongoDB
- Lazy loading for chat messages
- Async file processing
- Response compression
- Database connection pooling

### Best Practices
- Monitor API response times
- Optimize database queries
- Cache frequently accessed data
- Use CDN for static assets
- Implement pagination for large datasets

## 🐛 Troubleshooting

### Backend Issues

**Ollama connection failed**
```bash
# Ensure Ollama is running
ollama serve

# Check logs
# On Windows: Check %APPDATA%\Ollama
# On Mac: ~/Library/Application\ Support/Ollama
# On Linux: ~/.ollama
```

**MongoDB connection error**
```bash
# Check MongoDB is running
# For local: mongodb start
# For Atlas: Check connection string and IP whitelist
```

**Port already in use**
```bash
# Change port in config or kill process
# Windows: taskkill /PID <pid> /F
# Linux/Mac: kill -9 <pid>
```

### Frontend Issues

**API connection errors**
- Clear browser cache
- Check backend is running
- Verify `REACT_APP_API_URL` in `.env`
- Check console for CORS errors

**Build errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
npm run build
```

## 📚 Learning Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Ollama Models](https://ollama.ai/library)

### Libraries Used
- **Backend**: Flask, PyMongo, Sentence-Transformers, FAISS
- **Frontend**: React, Axios, Zustand, Tailwind CSS
- **AI**: Ollama, LangChain

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🎓 Educational Use

This platform is designed for educational institutions and can be customized for:
- School management
- College course delivery
- Corporate training
- Self-paced learning
- Tutoring platforms

## 🚀 Future Enhancements

- [ ] Video content support
- [ ] Collaborative learning features
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Social features (forums, discussions)
- [ ] Certification system
- [ ] Payment integration
- [ ] API documentation with Swagger
- [ ] Multi-language support
- [ ] Advanced RAG with semantic search

## ⭐ Acknowledgments

Built with ❤️ for educators and learners worldwide.

**Key Technologies:**
- OpenAI's Prompt Engineering patterns
- MongoDB's flexible schema
- FAISS's efficient similarity search
- HuggingFace's powerful NLP models
- React's component architecture
- Flask's lightweight framework

---

**Version**: 1.0.0
**Last Updated**: March 2026
**Status**: Production Ready ✅
