<!-- Authentication Flows -->

## Authentication Flow

### Sign Up
1. User enters email, password, name, role, institution
2. Frontend validates inputs (email format, password strength)
3. Frontend sends POST /auth/signup
4. Backend validates and checks if email exists
5. Backend hashes password with bcrypt
6. Backend creates user in MongoDB
7. Backend returns JWT token
8. Frontend stores token in localStorage
9. User redirected to dashboard

### Login
1. User enters email and password
2. Frontend validates inputs
3. Frontend sends POST /auth/login
4. Backend finds user by email
5. Backend verifies password against hash
6. Backend generates JWT token
7. Frontend stores token
8. User redirected to dashboard

### JWT Token Flow
- Token stored in localStorage
- Added to all API requests via Authorization header
- Verified on backend using Flask-JWT-Extended
- Auto-logout if token expires (401)
- Token refresh handled by frontend

---

## Document Processing Flow

### Upload Note (Teacher)
1. Teacher selects file (PDF, DOCX, TXT)
2. Frontend sends multipart/form-data with file
3. Backend receives file
4. Backend extracts text using appropriate parser:
   - PDF: PyPDF2
   - DOCX: python-docx
   - TXT: File read
5. Backend cleans and preprocesses text
6. Backend saves note to MongoDB
7. Backend chunks text into segments
8. Backend creates embeddings using Sentence-Transformers
9. Backend stores embeddings in FAISS vector DB
10. Note marked as "embeddings_stored"

### Retrieve and Search
1. User searches for note content
2. Frontend sends GET /notes/rag-search?q=query
3. Backend:
   - Encodes query using Sentence-Transformers
   - Searches FAISS index for similar chunks
   - Returns top-K results with similarity scores
   - Orders by relevance

---

## AI Chat Flow

### Chat Message Exchange
1. User types message
2. Frontend sends POST /chat/sessions/<id>/message
3. Backend:
   - Adds message to chat history
   - Retrieves last 5 messages for context
   - Searches vector DB for relevant learning materials
   - Builds RAG-augmented prompt
   - Calls Ollama API with MistralAI
   - Gets LLM response
   - Adds response to chat
   - Saves chat to MongoDB
4. Frontend receives response
5. Message displayed in chat UI with timestamp

### RAG Context Building
```
User Query → Vector Embeddings → FAISS Search → 
Top 3 Similar Chunks → Context Addition → 
Enhanced Prompt → LLM → Response
```

### Error Handling
- Ollama timeout: Return fallback response
- Model unavailable: Suggest alternatives
- Empty context: Generic response
- Hallucination prevention: Cite sources

---

## Assessment Submission Flow

### Take Assessment
1. Student clicks "Take Assessment"
2. Frontend fetches assessment questions
3. Student answers all questions
4. Student submits answers (POST /assessments/submit/<id>)
5. Backend:
   - Validates all questions answered
   - Calculates score by comparing answers
   - Stores attempts in progress
   - Calculates accuracy metrics
   - Updates student progress
   - Returns score and feedback
6. Frontend shows results and detailed feedback

### Score Calculation
```
Total Score = (Correct Answers × Marks / Total Marks) × 100
Passed = Score >= Passing Percentage
Accuracy = (Correct Answers / Total Questions) × 100
```

---

## Progress Tracking

### Update Progress
1. After assessment submission or Q&A evaluation
2. Backend updates progress document:
   - Increment total_questions_answered
   - Add to correct_answers count
   - Recalculate average_score
   - Update learning_streak
   - Record assessment entry
3. Store timestamps for activity tracking
4. Update leaderboard rankings

### Leaderboard Calculation
- Rank by average_score (descending)
- Filter by subject if specified
- Limit to top N students
- Include accuracy and question count
- Real-time updates

---

## File Upload Security

### Validation Steps
1. Check file extension (whitelist only)
2. Check file size (max 50MB)
3. Scan content (prevent executable files)
4. Store in secure folder
5. Generate unique filename (prevent overwriting)
6. Create file reference in database
7. Clean up if processing fails

### Supported Formats
- PDF (.pdf)
- Word (.docx, .doc)
- Text (.txt)

---

## Caching Strategy

### Cached Data
1. User profile (1 hour)
2. Published notes list (30 minutes)
3. Assessment questions (1 hour)
4. Vector embeddings (persistent)
5. Student progress (5 minutes)

### Cache Invalidation
- On data update (notes, assessments)
- On time expiration
- Manual refresh by admin
- On user logout

---

## Rate Limiting

### Applied To
- Authentication endpoints (10 requests/minute)
- Message sending (5 requests/minute)
- File uploads (2 requests/minute)
- Search queries (20 requests/minute)

### Response
- Returns 429 Too Many Requests
- Includes Retry-After header
- Clear error message to user

---

## Error Handling

### HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation error)
- **401**: Unauthorized (auth required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **409**: Conflict (duplicate email)
- **500**: Internal Server Error
- **503**: Service Unavailable (Ollama down)

### Error Response Format
```json
{
  "error": "Error message",
  "message": "Detailed message (optional)",
  "code": "ERROR_CODE"
}
```

---

## Input Validation

### User Input
- Email: RFC 5322 format
- Password: Min 8 chars, alphanumeric
- Name: Alphanumeric + spaces, max 255 chars
- Text input: Max 5000 chars, no script tags
- File input: Extension whitelist, size limit

### Injection Prevention
- Remove null bytes
- Strip script tags
- HTML encode special chars
- Parameterized queries for DB
- Input length limits

---

## Performance Monitoring

### Metrics Tracked
- API response time
- Database query time
- Cache hit ratio
- Error rate
- User sessions
- File upload success rate

### Optimization Techniques
- Database indexing
- Query optimization
- Connection pooling
- Lazy loading
- Pagination
- Response compression

---

This documentation covers the core workflows of the platform. For technical details, refer to code comments and API documentation.
