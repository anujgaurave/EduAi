import React, { useEffect, useState } from 'react';
import { useAuthStore, useProgressStore } from '../store';
import { progressAPI } from '../services/api';
import { FiTrendingUp, FiAward, FiZap, FiBook } from 'react-icons/fi';

function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      if (user?.role === 'student') {
        const response = await progressAPI.getStats();
        setStats(response.data.stats);
      }
    } catch (err) {
      console.error('Failed to load stats');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Welcome back, {user?.name}!</h1>
          <p className="text-gray-600 dark:text-gray-400">
            {user?.role === 'student'
              ? 'Continue your learning journey'
              : 'Manage your courses and students'}
          </p>
        </div>

        {/* Stats Grid */}
        {user?.role === 'student' && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon={<FiTrendingUp className="text-blue-600" size={24} />}
              title="Accuracy"
              value={`${stats.accuracy}%`}
              subtitle="Answer accuracy"
            />
            <StatCard
              icon={<FiAward className="text-purple-600" size={24} />}
              title="Assessments"
              value={stats.total_assessments}
              subtitle="Tests completed"
            />
            <StatCard
              icon={<FiZap className="text-yellow-600" size={24} />}
              title="Learning Streak"
              value={stats.learning_streak}
              subtitle="Days in a row"
            />
            <StatCard
              icon={<FiBook className="text-green-600" size={24} />}
              title="Questions"
              value={stats.total_questions_answered}
              subtitle="Total answered"
            />
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {user?.role === 'student' && (
            <>
              <ActionCard
                title="AI Chat Assistant"
                description="Ask questions and get instant responses based on your syllabus"
                buttonText="Start Chat"
                href="/chat"
              />
              <ActionCard
                title="Practice Assessments"
                description="Take quizzes and mock tests to evaluate your knowledge"
                buttonText="Take Assessment"
                href="/assessments"
              />
              <ActionCard
                title="Learning Materials"
                description="Access notes, documents, and resources uploaded by teachers"
                buttonText="Browse Notes"
                href="/notes"
              />
              <ActionCard
                title="Track Progress"
                description="View your performance metrics and learning analytics"
                buttonText="View Progress"
                href="/progress"
              />
            </>
          )}

          {user?.role === 'teacher' && (
            <>
              <ActionCard
                title="Upload Notes"
                description="Share PDFs, documents, and learning materials with students"
                buttonText="Upload"
                href="/notes"
              />
              <ActionCard
                title="Create Assessments"
                description="Design quizzes and tests with auto-generated questions"
                buttonText="Create"
                href="/assessments"
              />
              <ActionCard
                title="View Analytics"
                description="Monitor student performance and learning outcomes"
                buttonText="Analytics"
                href="/progress"
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, subtitle }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 flex items-center gap-4">
      <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">{icon}</div>
      <div>
        <p className="text-gray-600 dark:text-gray-400 text-sm">{title}</p>
        <h3 className="text-2xl font-bold">{value}</h3>
        <p className="text-gray-500 dark:text-gray-400 text-xs">{subtitle}</p>
      </div>
    </div>
  );
}

function ActionCard({ title, description, buttonText, href }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 flex flex-col gap-4">
      <div>
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        <p className="text-gray-600 dark:text-gray-400">{description}</p>
      </div>
      <a href={href} className="mt-auto">
        <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition">
          {buttonText}
        </button>
      </a>
    </div>
  );
}

export default DashboardPage;
