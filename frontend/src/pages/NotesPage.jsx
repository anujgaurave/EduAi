import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store';
import { notesAPI } from '../services/api';
import { FiUpload, FiSearch, FiDownload, FiTrash2, FiFile, FiX } from 'react-icons/fi';

function NotesPage() {
  const user = useAuthStore((state) => state.user);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    topic: '',
    description: '',
    file: null,
  });
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(null);

  const subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'History', 'English', 'Computer Science'];

  useEffect(() => {
    loadNotes();
  }, [selectedSubject]);

  const loadNotes = async () => {
    setLoading(true);
    try {
      // Teachers see their own notes, students see all published notes
      if (user?.role === 'teacher') {
        const response = await notesAPI.getTeacherNotes(user._id);
        setNotes(response.data.notes);
      } else {
        const response = await notesAPI.getNotes(selectedSubject);
        setNotes(response.data.notes);
      }
    } catch (err) {
      setError('Failed to load notes');
      setTimeout(() => setError(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadNotes();
      return;
    }
    setLoading(true);
    try {
      const response = await notesAPI.searchNotes(searchQuery);
      setNotes(response.data.results);
    } catch (err) {
      setError('Search failed');
      setTimeout(() => setError(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!formData.file) {
      setError('Please select a file');
      return;
    }
    const uploadFormData = new FormData();
    uploadFormData.append('file', formData.file);
    uploadFormData.append('title', formData.title);
    uploadFormData.append('subject', formData.subject);
    uploadFormData.append('topic', formData.topic);
    uploadFormData.append('description', formData.description);

    setLoading(true);
    try {
      const response = await notesAPI.uploadNote(uploadFormData);
      setNotes([response.data.note, ...notes]);
      setShowUploadForm(false);
      setFormData({ title: '', subject: '', topic: '', description: '', file: null });
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
      setTimeout(() => setError(''), 4000);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (note) => {
    setDownloading(note._id);
    try {
      const response = await notesAPI.downloadNote(note._id);
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Try to get filename from Content-Disposition header
      const contentDisposition = response.headers['content-disposition'];
      let filename = note.title + '.' + note.file_type;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^";\n]+)"?/);
        if (match) filename = match[1];
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Download failed. File may not exist on server.');
      setTimeout(() => setError(''), 4000);
    } finally {
      setDownloading(null);
    }
  };

  const handleDelete = async (noteId) => {
    if (!window.confirm('Delete this note?')) return;
    try {
      await notesAPI.deleteNote(noteId);
      setNotes(notes.filter((n) => n._id !== noteId));
    } catch (err) {
      setError('Failed to delete note');
      setTimeout(() => setError(''), 3000);
    }
  };

  const getFileIcon = (fileType) => {
    const icons = { pdf: '📄', docx: '📝', doc: '📝', txt: '📃' };
    return icons[fileType] || '📄';
  };

  return (
    <div className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <h1 className="text-3xl font-bold text-white mb-4 md:mb-0">Learning Materials</h1>
          {user?.role === 'teacher' && (
            <button
              onClick={() => setShowUploadForm(!showUploadForm)}
              className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl flex items-center gap-2 w-full md:w-auto justify-center font-semibold transition"
            >
              <FiUpload /> Upload Note
            </button>
          )}
        </div>

        {/* Upload Form */}
        {showUploadForm && user?.role === 'teacher' && (
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4">Upload Learning Material</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Subject</label>
                  <select
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select Subject</option>
                    {subjects.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Topic</label>
                  <input
                    type="text"
                    value={formData.topic}
                    onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                  rows="2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">File (PDF, DOCX, TXT)</label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.doc"
                  onChange={(e) => setFormData({ ...formData, file: e.target.files[0] })}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-gray-300 rounded-xl"
                  required
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 text-white font-semibold py-2.5 rounded-xl transition"
                >
                  {loading ? 'Uploading...' : 'Upload'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUploadForm(false)}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-xl transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Search and Filter */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-4 mb-8">
          <div className="flex gap-3 flex-col md:flex-row">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search notes..."
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white placeholder-gray-400 rounded-xl focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={handleSearch}
              className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-xl flex items-center gap-2 transition"
            >
              <FiSearch /> Search
            </button>
          </div>
          {user?.role !== 'teacher' && (
            <div className="mt-3 flex gap-2 flex-wrap">
              {subjects.map((subject) => (
                <button
                  key={subject}
                  onClick={() => setSelectedSubject(selectedSubject === subject ? '' : subject)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition ${
                    selectedSubject === subject
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {subject}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Notes Grid */}
        {loading ? (
          <div className="flex justify-center py-16">
            <div className="spinner"></div>
          </div>
        ) : notes.length === 0 ? (
          <div className="text-center py-16">
            <FiFile size={48} className="mx-auto text-gray-600 mb-4" />
            <p className="text-gray-400 text-lg">
              {user?.role === 'teacher' ? 'No notes uploaded yet' : 'No notes found'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {notes.map((note) => (
              <div
                key={note._id}
                className="bg-gray-800 border border-gray-700 rounded-2xl p-6 hover:border-gray-500 transition-all duration-200"
              >
                <div className="flex items-start gap-3 mb-3">
                  <span className="text-2xl">{getFileIcon(note.file_type)}</span>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-bold text-white truncate">{note.title}</h3>
                    <p className="text-sm text-blue-400">{note.subject}</p>
                  </div>
                </div>
                {note.topic && (
                  <p className="text-xs text-gray-500 mb-2">Topic: {note.topic}</p>
                )}
                <p className="text-gray-400 text-sm mb-4 line-clamp-2">{note.description}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleDownload(note)}
                    disabled={downloading === note._id}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white py-2 rounded-xl flex items-center justify-center gap-2 text-sm font-medium transition"
                  >
                    <FiDownload size={14} />
                    {downloading === note._id ? 'Downloading...' : 'Download'}
                  </button>
                  {user?.role === 'teacher' && (
                    <button
                      onClick={() => handleDelete(note._id)}
                      className="bg-red-600/20 hover:bg-red-600 border border-red-600/40 text-red-400 hover:text-white px-3 py-2 rounded-xl transition"
                    >
                      <FiTrash2 size={14} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="fixed bottom-6 right-6 bg-red-500 text-white px-5 py-3 rounded-xl shadow-xl flex items-center gap-2">
            <FiX size={16} /> {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default NotesPage;
