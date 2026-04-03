import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store';
import { useNavigate } from 'react-router-dom';
import { assessmentAPI } from '../services/api';
import { FiPlus, FiPlay, FiCheckCircle, FiX, FiEye, FiSend } from 'react-icons/fi';

function AssessmentsPage() {
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [submissionsModal, setSubmissionsModal] = useState({ open: false, assessmentId: null, data: [], loading: false, assessmentTitle: '' });
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    description: '',
    duration_minutes: 60,
    passing_percentage: 40,
    questions: [{ question_text: '', options: ['', '', '', ''], correct_answer: 0, marks: 1 }],
  });
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [publishing, setPublishing] = useState(null);

  useEffect(() => {
    loadAssessments();
  }, [user]);

  const loadAssessments = async () => {
    if (!user) return;
    setLoading(true);
    try {
      if (user.role === 'student') {
        const response = await assessmentAPI.getAvailableAssessments();
        setAssessments(response.data.assessments || []);
      } else if (user.role === 'teacher') {
        // Teachers: fetch from DB directly via teacher endpoint
        // We reuse getTeacherAssessments logic via a raw API call
        const response = await assessmentAPI.getTeacherAssessments();
        setAssessments(response.data.assessments || []);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load assessments');
      setTimeout(() => setError(''), 4000);
    } finally {
      setLoading(false);
    }
  };

  const handleAddQuestion = () => {
    setFormData({
      ...formData,
      questions: [
        ...formData.questions,
        { question_text: '', options: ['', '', '', ''], correct_answer: 0, marks: 1 },
      ],
    });
  };

  const handleRemoveQuestion = (index) => {
    if (formData.questions.length === 1) return;
    const newQuestions = formData.questions.filter((_, i) => i !== index);
    setFormData({ ...formData, questions: newQuestions });
  };

  const handleQuestionChange = (index, field, value) => {
    const newQuestions = [...formData.questions];
    newQuestions[index][field] = value;
    setFormData({ ...formData, questions: newQuestions });
  };

  const handleOptionChange = (qIndex, oIndex, value) => {
    const newQuestions = [...formData.questions];
    newQuestions[qIndex].options[oIndex] = value;
    setFormData({ ...formData, questions: newQuestions });
  };

  const handleCreateAssessment = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (editingId) {
        await assessmentAPI.updateAssessment(editingId, {
          title: formData.title,
          subject: formData.subject,
          description: formData.description,
          duration_minutes: formData.duration_minutes,
          passing_percentage: formData.passing_percentage,
          questions: formData.questions,
        });
        setSuccessMsg('Assessment updated successfully!');
      } else {
        await assessmentAPI.createAssessment({
          title: formData.title,
          subject: formData.subject,
          description: formData.description,
          duration_minutes: formData.duration_minutes,
          passing_percentage: formData.passing_percentage,
          questions: formData.questions,
        });
        setSuccessMsg('Assessment created! Publish it to make it visible to students.');
      }
      
      setShowCreateForm(false);
      setEditingId(null);
      setFormData({
        title: '',
        subject: '',
        description: '',
        duration_minutes: 60,
        passing_percentage: 40,
        questions: [{ question_text: '', options: ['', '', '', ''], correct_answer: 0, marks: 1 }],
      });
      setSuccessMsg('Assessment created! Publish it to make it visible to students.');
      setTimeout(() => setSuccessMsg(''), 5000);
      loadAssessments();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create assessment');
      setTimeout(() => setError(''), 4000);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async (assessmentId) => {
    setPublishing(assessmentId);
    try {
      await assessmentAPI.publishAssessment(assessmentId);
      setAssessments((prev) =>
        prev.map((a) => (a._id === assessmentId ? { ...a, is_published: true } : a))
      );
      setSuccessMsg('Assessment published! Students can now see it.');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError('Failed to publish assessment');
      setTimeout(() => setError(''), 3000);
    } finally {
      setPublishing(null);
    }
  };

  const handleViewSubmissions = async (assessment) => {
    setSubmissionsModal({ open: true, assessmentId: assessment._id, data: [], loading: true, assessmentTitle: assessment.title });
    try {
      const response = await assessmentAPI.getAssessmentSubmissions(assessment._id);
      setSubmissionsModal({ open: true, assessmentId: assessment._id, data: response.data.submissions, loading: false, assessmentTitle: assessment.title });
    } catch (err) {
      setError('Failed to load submissions');
      setTimeout(() => setError(''), 3000);
      setSubmissionsModal({ open: false, assessmentId: null, data: [], loading: false, assessmentTitle: '' });
    }
  };

  const handleAllowReattempt = async (studentId) => {
    if (!window.confirm("Are you sure you want to delete this student's submission and allow them to take the assessment again?")) return;
    
    try {
      await assessmentAPI.allowReattempt(submissionsModal.assessmentId, studentId);
      setSuccessMsg('Student can now reattempt the assessment');
      setTimeout(() => setSuccessMsg(''), 3000);
      
      // Remove from current modal view
      setSubmissionsModal(prev => ({
        ...prev,
        data: prev.data.filter(s => s.student_id !== studentId)
      }));
    } catch (err) {
      setError('Failed to allow reattempt');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleEditClick = (assessment) => {
    setEditingId(assessment._id);
    setFormData({
      title: assessment.title || '',
      subject: assessment.subject || '',
      description: assessment.description || '',
      duration_minutes: assessment.duration_minutes || 60,
      passing_percentage: assessment.passing_percentage || 40,
      questions: assessment.questions?.length ? assessment.questions : [{ question_text: '', options: ['', '', '', ''], correct_answer: 0, marks: 1 }],
    });
    setShowCreateForm(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <h1 className="text-3xl font-bold text-white mb-4 md:mb-0">Assessments & Quizzes</h1>
          {user?.role === 'teacher' && (
            <button
              onClick={() => {
                setEditingId(null);
                setFormData({
                  title: '',
                  subject: '',
                  description: '',
                  duration_minutes: 60,
                  passing_percentage: 40,
                  questions: [{ question_text: '', options: ['', '', '', ''], correct_answer: 0, marks: 1 }],
                });
                setShowCreateForm(!showCreateForm);
              }}
              className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl flex items-center gap-2 w-full md:w-auto justify-center font-semibold transition"
            >
              <FiPlus /> Create Assessment
            </button>
          )}
        </div>

        {/* Teacher hint */}
        {user?.role === 'teacher' && (
          <div className="bg-blue-600/10 border border-blue-500/30 rounded-xl p-4 mb-6 text-blue-300 text-sm">
            💡 After creating an assessment, click <strong>Publish</strong> to make it visible to students.
          </div>
        )}

        {/* Create Form */}
        {showCreateForm && user?.role === 'teacher' && (
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4">{editingId ? 'Edit Assessment' : 'Create New Assessment'}</h2>
            <form onSubmit={handleCreateAssessment} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Title</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Subject</label>
                  <input
                    type="text"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                    required
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
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Duration (minutes)</label>
                  <input
                    type="number"
                    value={formData.duration_minutes}
                    onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                    min="1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Passing % </label>
                  <input
                    type="number"
                    value={formData.passing_percentage}
                    onChange={(e) => setFormData({ ...formData, passing_percentage: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                    min="1" max="100"
                  />
                </div>
              </div>

              {/* Questions */}
              <div>
                <h3 className="text-base font-semibold text-white mb-3">Questions</h3>
                {formData.questions.map((q, qIndex) => (
                  <div key={qIndex} className="border border-gray-600 rounded-xl p-4 mb-4 bg-gray-700/40">
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-sm font-medium text-gray-300">Question {qIndex + 1}</span>
                      {formData.questions.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveQuestion(qIndex)}
                          className="text-red-400 hover:text-red-300 text-xs"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                    <textarea
                      value={q.question_text}
                      onChange={(e) => handleQuestionChange(qIndex, 'question_text', e.target.value)}
                      className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500 mb-3"
                      rows="2"
                      placeholder="Enter question..."
                      required
                    />
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
                      {q.options.map((option, oIndex) => (
                        <input
                          key={oIndex}
                          type="text"
                          placeholder={`Option ${String.fromCharCode(65 + oIndex)}`}
                          value={option}
                          onChange={(e) => handleOptionChange(qIndex, oIndex, e.target.value)}
                          className="px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      ))}
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">Correct Answer</label>
                        <select
                          value={q.correct_answer}
                          onChange={(e) => handleQuestionChange(qIndex, 'correct_answer', parseInt(e.target.value))}
                          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                        >
                          {q.options.map((_, idx) => (
                            <option key={idx} value={idx}>Option {String.fromCharCode(65 + idx)}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">Marks</label>
                        <input
                          type="number"
                          value={q.marks}
                          onChange={(e) => handleQuestionChange(qIndex, 'marks', parseInt(e.target.value))}
                          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-xl focus:ring-2 focus:ring-blue-500"
                          min="1"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={handleAddQuestion}
                  className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 mb-4 transition"
                >
                  <FiPlus size={14} /> Add Another Question
                </button>
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 text-white font-semibold py-2.5 rounded-xl transition"
                >
                  {loading ? (editingId ? 'Updating...' : 'Creating...') : (editingId ? 'Update Assessment' : 'Create Assessment')}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-xl transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Assessment List */}
        {loading ? (
          <div className="flex justify-center py-16">
            <div className="spinner"></div>
          </div>
        ) : assessments.length === 0 ? (
          <div className="text-center py-16">
            <FiCheckCircle size={48} className="mx-auto text-gray-600 mb-4" />
            <p className="text-gray-400 text-lg">
              {user?.role === 'teacher' ? 'No assessments created yet' : 'No assessments available'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {assessments.map((assessment) => (
              <div
                key={assessment._id}
                className="bg-gray-800 border border-gray-700 rounded-2xl p-6 hover:border-gray-500 transition-all duration-200"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-bold text-white">{assessment.title}</h3>
                  {user?.role === 'teacher' && (
                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                      assessment.is_published
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                        : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                    }`}>
                      {assessment.is_published ? 'Published' : 'Draft'}
                    </span>
                  )}
                </div>
                <p className="text-gray-400 text-sm mb-4">{assessment.description}</p>
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-400 mb-5">
                  <p>📚 <span className="text-gray-300">{assessment.subject}</span></p>
                  <p>❓ <span className="text-gray-300">{assessment.questions?.length || 0} questions</span></p>
                  <p>⏱ <span className="text-gray-300">{assessment.duration_minutes} mins</span></p>
                  <p>🎯 <span className="text-gray-300">Pass: {assessment.passing_percentage}%</span></p>
                </div>

                {user?.role === 'student' && (
                  assessment.is_completed ? (
                    <button 
                      disabled
                      className="w-full bg-gray-700 text-gray-400 py-2.5 rounded-xl flex items-center justify-center gap-2 font-medium cursor-not-allowed"
                    >
                      <FiCheckCircle size={14} /> Submitted
                    </button>
                  ) : (
                    <button 
                      onClick={() => navigate(`/assessments/take/${assessment._id}`)}
                      className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-xl flex items-center justify-center gap-2 font-medium transition"
                    >
                      <FiPlay size={14} /> Take Assessment
                    </button>
                  )
                )}

                {user?.role === 'teacher' && (
                  <div className="grid grid-cols-2 gap-2 mt-4">
                    <button
                      onClick={() => handleViewSubmissions(assessment)}
                      className="w-full bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 py-2.5 rounded-xl flex items-center justify-center gap-2 font-medium transition"
                    >
                      <FiEye size={14} /> Submissions
                    </button>
                    <button
                      onClick={() => handleEditClick(assessment)}
                      className="w-full bg-gray-700/50 hover:bg-gray-700 border border-gray-600 text-gray-300 py-2.5 rounded-xl flex items-center justify-center gap-2 font-medium transition"
                    >
                      Edit
                    </button>
                  </div>
                )}
                
                {user?.role === 'teacher' && !assessment.is_published && (
                  <button
                    onClick={() => handlePublish(assessment._id)}
                    disabled={publishing === assessment._id}
                    className="w-full mt-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-600 text-white py-2.5 rounded-xl flex items-center justify-center gap-2 font-medium transition"
                  >
                    <FiSend size={14} />
                    {publishing === assessment._id ? 'Publishing...' : 'Publish to Students'}
                  </button>
                )}
                {user?.role === 'teacher' && assessment.is_published && (
                  <div className="flex items-center gap-2 text-green-400 text-sm">
                    <FiCheckCircle size={14} /> Visible to students
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Toasts */}
        {error && (
          <div className="fixed bottom-6 right-6 bg-red-500 text-white px-5 py-3 rounded-xl shadow-xl flex items-center gap-2">
            <FiX size={16} /> {error}
          </div>
        )}
        {successMsg && (
          <div className="fixed bottom-6 right-6 bg-green-600 text-white px-5 py-3 rounded-xl shadow-xl flex items-center gap-2">
            <FiCheckCircle size={16} /> {successMsg}
          </div>
        )}
        {/* Submissions Modal */}
        {submissionsModal.open && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 w-full max-w-4xl max-h-[80vh] flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white">Submissions</h2>
                  <p className="text-gray-400 text-sm mt-1">{submissionsModal.assessmentTitle}</p>
                </div>
                <button 
                  onClick={() => setSubmissionsModal({ open: false, assessmentId: null, data: [], loading: false, assessmentTitle: '' })}
                  className="p-2 hover:bg-gray-700 rounded-lg transition text-gray-400 hover:text-white"
                >
                  <FiX size={20} />
                </button>
              </div>
              
              <div className="flex-1 overflow-auto overflow-y-auto pr-2 rounded-xl border border-gray-700 bg-gray-900/50 scrollbar-thin">
                {submissionsModal.loading ? (
                  <div className="flex justify-center items-center py-12">
                    <div className="spinner"></div>
                  </div>
                ) : submissionsModal.data.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    <FiEye size={36} className="mx-auto mb-3 opacity-50" />
                    <p>No submissions found yet.</p>
                  </div>
                ) : (
                  <table className="w-full text-left text-sm text-gray-300">
                    <thead className="text-xs text-gray-400 uppercase bg-gray-800 border-b border-gray-700 sticky top-0">
                      <tr>
                        <th className="px-6 py-4 rounded-tl-xl">Student Name</th>
                        <th className="px-6 py-4">Score</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Completed At</th>
                        <th className="px-6 py-4 rounded-tr-xl">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {submissionsModal.data.map((sub, i) => (
                        <tr key={i} className="border-b border-gray-700/50 hover:bg-gray-800/50 transition">
                          <td className="px-6 py-4 font-medium text-white">
                            {sub.student_name}
                            <div className="text-xs text-gray-500 mt-1">{sub.student_email}</div>
                          </td>
                          <td className="px-6 py-4">
                            <span className="font-bold">{sub.score}%</span>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                              sub.passed ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
                            }`}>
                              {sub.passed ? 'Passed' : 'Failed'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-gray-400 text-xs">
                            {new Date(sub.date).toLocaleString()}
                          </td>
                          <td className="px-6 py-4">
                            <button
                              onClick={() => handleAllowReattempt(sub.student_id)}
                              className="text-xs bg-red-500/10 hover:bg-red-500/20 text-red-400 px-3 py-1.5 rounded-lg border border-red-500/20 transition"
                            >
                              Allow Reattempt
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default AssessmentsPage;
