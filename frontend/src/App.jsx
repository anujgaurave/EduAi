import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store';

// Pages
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import NotesPage from './pages/NotesPage';
import AssessmentsPage from './pages/AssessmentsPage';
import TakeAssessmentPage from './pages/TakeAssessmentPage';
import ProfilePage from './pages/ProfilePage';
import ProgressPage from './pages/ProgressPage';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import Navigation from './components/Navigation';

function App() {
  const user = useAuthStore((state) => state.user);
  const token = useAuthStore((state) => state.token);
  const logout = useAuthStore((state) => state.logout);

  // Force dark mode permanently
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  useEffect(() => {
    if (token && !user) {
      useAuthStore.getState().getProfile()
        .catch((error) => {
          if (error.response?.status === 422 || error.response?.status === 401) {
            logout();
          }
        });
    }
  }, [token, user, logout]);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gray-900 text-white">
        {token && <Navigation />}
        
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={!token ? <LoginPage /> : <Navigate to="/dashboard" />} />
          <Route path="/signup" element={!token ? <SignupPage /> : <Navigate to="/dashboard" />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={<ProtectedRoute><DashboardPage /></ProtectedRoute>}
          />
          <Route
            path="/chat/:chatId?"
            element={<ProtectedRoute><ChatPage /></ProtectedRoute>}
          />
          <Route
            path="/notes"
            element={<ProtectedRoute><NotesPage /></ProtectedRoute>}
          />
          <Route
            path="/assessments"
            element={<ProtectedRoute><AssessmentsPage /></ProtectedRoute>}
          />
          <Route
            path="/assessments/take/:assessmentId"
            element={<ProtectedRoute><TakeAssessmentPage /></ProtectedRoute>}
          />
          <Route
            path="/progress"
            element={<ProtectedRoute><ProgressPage /></ProtectedRoute>}
          />
          <Route
            path="/profile"
            element={<ProtectedRoute><ProfilePage /></ProtectedRoute>}
          />

          {/* Default Route */}
          <Route path="/" element={token ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
