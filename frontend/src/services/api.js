import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  signup: (email, password, name, role, institution = '') =>
    api.post('/auth/signup', { email, password, name, role, institution }),
  
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  
  getProfile: () =>
    api.get('/auth/profile'),
  
  updateProfile: (profile) =>
    api.put('/auth/profile', { profile }),
  
  changePassword: (oldPassword, newPassword) =>
    api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
  
  deactivateAccount: () =>
    api.post('/auth/deactivate'),
};

// Chat APIs
export const chatAPI = {
  getSessions: (page = 1, limit = 20) =>
    api.get('/chat/sessions', { params: { page, limit } }),
  
  createSession: (title = 'New Chat') =>
    api.post('/chat/sessions', { title }),
  
  getChat: (chatId) =>
    api.get(`/chat/sessions/${chatId}`),
  
  sendMessage: (chatId, message) =>
    api.post(`/chat/sessions/${chatId}/message`, { message }),
  
  deleteChat: (chatId) =>
    api.delete(`/chat/sessions/${chatId}`),
  
  updateChatTitle: (chatId, title) =>
    api.put(`/chat/sessions/${chatId}/title`, { title }),
  
  searchChats: (query) =>
    api.get('/chat/search', { params: { q: query } }),
};

// Notes APIs
export const notesAPI = {
  uploadNote: (formData) =>
    api.post('/notes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  getNotes: (subject = '', page = 1, limit = 20) =>
    api.get('/notes', { params: { subject, page, limit } }),
  
  getNote: (noteId) =>
    api.get(`/notes/${noteId}`),
  
  getTeacherNotes: (teacherId) =>
    api.get(`/notes/teacher/${teacherId}`),
  
  deleteNote: (noteId) =>
    api.delete(`/notes/${noteId}`),
  
  downloadNote: (noteId) =>
    api.get(`/notes/download/${noteId}`, { responseType: 'blob' }),
  
  searchNotes: (query) =>
    api.get('/notes/search', { params: { q: query } }),
  
  ragSearch: (query) =>
    api.get('/notes/rag-search', { params: { q: query } }),
};

// Assessment APIs
export const assessmentAPI = {
  createAssessment: (assessmentData) =>
    api.post('/assessments/create', assessmentData),
  
  getAssessment: (assessmentId) =>
    api.get(`/assessments/${assessmentId}`),
  
  publishAssessment: (assessmentId) =>
    api.post(`/assessments/publish/${assessmentId}`),
  
  submitAssessment: (assessmentId, answers) =>
    api.post(`/assessments/submit/${assessmentId}`, { answers }),
  
  generateQuiz: (topic, numQuestions = 5, difficulty = 'medium') =>
    api.post('/assessments/generate-quiz', {
      topic,
      num_questions: numQuestions,
      difficulty,
    }),
  
  getAvailableAssessments: () =>
    api.get('/assessments/available'),
  
  getTeacherAssessments: () =>
    api.get('/assessments/my-assessments'),
    
  getAssessmentSubmissions: (assessmentId) =>
    api.get(`/assessments/${assessmentId}/submissions`),
    
  updateAssessment: (assessmentId, data) =>
    api.put(`/assessments/${assessmentId}`, data),
    
  allowReattempt: (assessmentId, studentId) =>
    api.delete(`/assessments/${assessmentId}/submissions/${studentId}`),
};

// Progress APIs
export const progressAPI = {
  getMyProgress: () =>
    api.get('/progress/my-progress'),
  
  getStudentProgress: (studentId) =>
    api.get(`/progress/student/${studentId}`),
  
  getStats: () =>
    api.get('/progress/stats'),
  
  updateScore: (correct, total) =>
    api.post('/progress/update-score', { correct, total }),
  
  getLeaderboard: (limit = 10, subject = '') =>
    api.get('/progress/leaderboard', { params: { limit, subject } }),
};

export default api;
