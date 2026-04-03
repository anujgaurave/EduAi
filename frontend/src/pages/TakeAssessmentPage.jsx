import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assessmentAPI } from '../services/api';
import { FiClock, FiCheckCircle, FiChevronRight, FiChevronLeft, FiSend, FiAlertCircle } from 'react-icons/fi';

function TakeAssessmentPage() {
  const { assessmentId } = useParams();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({}); // { question_id: selected_option_index }
  const [timeLeft, setTimeLeft] = useState(0);
  
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null); // { score, total_marks, passed, ... }

  useEffect(() => {
    loadAssessment();
  }, [assessmentId]);

  useEffect(() => {
    if (assessment && !result && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            handleSubmit(new Event('submit'));
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [assessment, result, timeLeft]);

  const loadAssessment = async () => {
    setLoading(true);
    try {
      const response = await assessmentAPI.getAssessment(assessmentId);
      setAssessment(response.data.assessment);
      setTimeLeft(response.data.assessment.duration_minutes * 60);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load assessment');
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (qId, optionIndex) => {
    if (result) return; // Prevent changing after submit
    setAnswers({
      ...answers,
      [qId]: optionIndex
    });
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (submitting || result) return;
    
    // Check if all questions are answered, though we can allow partial
    const qCount = assessment.questions.length;
    const answeredCount = Object.keys(answers).length;
    
    if (answeredCount < qCount && e?.isTrusted) {
      if (!window.confirm(`You have only answered ${answeredCount} of ${qCount} questions. Submit anyway?`)) {
        return;
      }
    }

    setSubmitting(true);
    try {
      const response = await assessmentAPI.submitAssessment(assessmentId, answers);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit assessment');
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] bg-gray-900 flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="min-h-[calc(100vh-64px)] bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <FiAlertCircle size={48} className="mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Oops!</h2>
          <p className="text-gray-400">{error || 'Assessment not found'}</p>
          <button 
            onClick={() => navigate('/assessments')}
            className="mt-6 px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (result) {
    return (
      <div className="min-h-[calc(100vh-64px)] bg-gray-900 py-12 px-4 flex items-center justify-center">
        <div className="max-w-md w-full bg-gray-800 border border-gray-700 rounded-3xl p-8 text-center">
          <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 ${result.passed ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
            {result.passed ? <FiCheckCircle size={40} /> : <FiAlertCircle size={40} />}
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">
            {result.passed ? 'Assessment Passed!' : 'Assessment Failed'}
          </h1>
          <p className="text-gray-400 mb-8">{assessment.title}</p>
          
          <div className="bg-gray-900 rounded-2xl p-6 mb-8">
            <div className="text-5xl font-bold text-white mb-2">
              {result.score}%
            </div>
            <p className="text-sm text-gray-500">
              Required to pass: {result.passing_percentage}%
            </p>
            <div className="mt-4 pt-4 border-t border-gray-800 grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Total Marks</p>
                <p className="text-lg font-semibold text-white">{result.total_marks}</p>
              </div>
              <div>
                <p className="text-gray-500">Correct Marks</p>
                <p className="text-lg font-semibold text-white">{result.correct_answers}</p>
              </div>
            </div>
          </div>
          
          <button 
            onClick={() => navigate('/assessments')}
            className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition"
          >
            Back to Assessments
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = assessment.questions[currentQuestionIndex];

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gray-900 py-8 px-4 flex flex-col items-center">
      <div className="max-w-3xl w-full">
        {/* Header */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-5 mb-6 flex flex-col sm:flex-row justify-between items-center gap-4 sticky top-4 z-10 shadow-xl shadow-gray-900/50">
          <div>
            <h1 className="text-lg font-bold text-white">{assessment.title}</h1>
            <p className="text-sm text-gray-400">Question {currentQuestionIndex + 1} of {assessment.questions.length}</p>
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono text-lg font-bold ${
            timeLeft < 60 ? 'bg-red-500/20 text-red-400 animate-pulse' : 'bg-blue-600/20 text-blue-400'
          }`}>
            <FiClock /> {formatTime(timeLeft)}
          </div>
        </div>

        {/* Question Area */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 md:p-8 mb-6">
          <div className="flex gap-4 mb-8">
            <div className="w-10 h-10 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold flex-shrink-0 text-lg">
              {currentQuestionIndex + 1}
            </div>
            <div className="pt-1.5">
              <h2 className="text-xl font-medium text-white leading-relaxed">
                {currentQuestion.question_text}
              </h2>
              {currentQuestion.marks > 0 && (
                <span className="inline-block mt-3 text-xs font-semibold px-2.5 py-1 bg-gray-700 text-gray-300 rounded-lg">
                  {currentQuestion.marks} Mark{currentQuestion.marks > 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>

          <div className="space-y-3 pl-14">
            {currentQuestion.options.map((option, idx) => {
              const isSelected = answers[currentQuestion._id] === idx;
              return (
                <button
                  key={idx}
                  onClick={() => handleOptionSelect(currentQuestion._id, idx)}
                  className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-200 flex items-center gap-4 ${
                    isSelected 
                      ? 'border-blue-500 bg-blue-600/10' 
                      : 'border-gray-700 hover:border-gray-500 bg-gray-700/30'
                  }`}
                >
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'border-blue-500' : 'border-gray-500'
                  }`}>
                    {isSelected && <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />}
                  </div>
                  <span className={`text-base ${isSelected ? 'text-blue-100 font-medium' : 'text-gray-300'}`}>
                    {option}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="flex justify-between items-center bg-gray-800 border border-gray-700 rounded-2xl p-4">
          <button
            onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentQuestionIndex === 0}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-white bg-gray-700 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <FiChevronLeft size={18} /> Previous
          </button>
          
          {currentQuestionIndex < assessment.questions.length - 1 ? (
            <button
              onClick={() => setCurrentQuestionIndex((prev) => Math.min(assessment.questions.length - 1, prev + 1))}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-white bg-blue-600 hover:bg-blue-500 transition"
            >
              Next <FiChevronRight size={18} />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-white bg-green-600 hover:bg-green-500 transition shadow-lg shadow-green-900/40"
            >
              {submitting ? 'Submitting...' : 'Submit Assessment'} <FiSend size={18} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default TakeAssessmentPage;
