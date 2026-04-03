import { create } from 'zustand';
import { authAPI } from '../services/api';

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('access_token') || null,
  loading: false,
  error: null,

  signup: async (email, password, name, role, institution) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.signup(email, password, name, role, institution);
      localStorage.setItem('access_token', response.data.access_token);
      set({
        user: response.data.user,
        token: response.data.access_token,
        loading: false,
      });
      return response.data;
    } catch (error) {
      set({
        error: error.response?.data?.error || 'Signup failed',
        loading: false,
      });
      throw error;
    }
  },

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.login(email, password);
      localStorage.setItem('access_token', response.data.access_token);
      set({
        user: response.data.user,
        token: response.data.access_token,
        loading: false,
      });
      return response.data;
    } catch (error) {
      set({
        error: error.response?.data?.error || 'Login failed',
        loading: false,
      });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null });
  },

  getProfile: async () => {
    try {
      const response = await authAPI.getProfile();
      set({ user: response.data.user });
      return response.data.user;
    } catch (error) {
      set({ error: error.response?.data?.error || 'Failed to fetch profile' });
      throw error;
    }
  },

  updateProfile: async (profile) => {
    try {
      const response = await authAPI.updateProfile(profile);
      set({ user: response.data.user });
      return response.data.user;
    } catch (error) {
      set({ error: error.response?.data?.error || 'Failed to update profile' });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));

export const useChatStore = create((set) => ({
  chats: [],
  currentChat: null,
  loading: false,
  error: null,

  setChats: (chats) => set({ chats }),
  setCurrentChat: (chat) => set({ currentChat: chat }),

  addMessage: (message) =>
    set((state) => ({
      currentChat: {
        ...state.currentChat,
        messages: [...(state.currentChat?.messages || []), message],
      },
    })),

  clearChat: () => set({ currentChat: null }),
}));

export const useNoteStore = create((set) => ({
  notes: [],
  loading: false,
  error: null,

  setNotes: (notes) => set({ notes }),
  addNote: (note) =>
    set((state) => ({ notes: [note, ...state.notes] })),
  removeNote: (noteId) =>
    set((state) => ({
      notes: state.notes.filter((n) => n._id !== noteId),
    })),
}));

export const useAssessmentStore = create((set) => ({
  assessments: [],
  currentAssessment: null,
  loading: false,
  error: null,

  setAssessments: (assessments) => set({ assessments }),
  setCurrentAssessment: (assessment) => set({ currentAssessment: assessment }),
}));

export const useProgressStore = create((set) => ({
  progress: null,
  stats: null,
  leaderboard: [],
  loading: false,
  error: null,

  setProgress: (progress) => set({ progress }),
  setStats: (stats) => set({ stats }),
  setLeaderboard: (leaderboard) => set({ leaderboard }),
}));

export const useThemeStore = create(() => ({
  isDark: true, // Always dark - light mode removed
  toggleTheme: () => {}, // No-op: dark mode is permanent
}));
