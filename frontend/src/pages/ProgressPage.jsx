import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store';
import { progressAPI } from '../services/api';
import { FiTrendingUp, FiAward, FiTarget } from 'react-icons/fi';

function ProgressPage() {
  const user = useAuthStore((state) => state.user);
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      if (user?.role === 'student') {
        const statsRes = await progressAPI.getStats();
        setStats(statsRes.data.stats);
      }
      const leaderboardRes = await progressAPI.getLeaderboard(10);
      setLeaderboard(leaderboardRes.data.leaderboard);
    } catch (err) {
      setError('Failed to load progress data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Progress & Analytics</h1>

        {/* Personal Stats */}
        {user?.role === 'student' && stats && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Your Statistics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatBox
                icon={<FiTrendingUp className="text-green-600" size={28} />}
                label="Accuracy"
                value={`${stats.accuracy}%`}
                color="green"
              />
              <StatBox
                icon={<FiTarget className="text-blue-600" size={28} />}
                label="Questions Answered"
                value={stats.total_questions_answered}
                color="blue"
              />
              <StatBox
                icon={<FiAward className="text-purple-600" size={28} />}
                label="Assessments"
                value={stats.total_assessments}
                color="purple"
              />
              <StatBox
                icon={<FiTrendingUp className="text-yellow-600" size={28} />}
                label="Avg Score"
                value={`${Math.round(stats.average_assessment_score)}%`}
                color="yellow"
              />
            </div>
          </div>
        )}

        {/* Leaderboard */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-6">Top Performers</h2>
          {loading ? (
            <div className="flex justify-center">
              <div className="spinner"></div>
            </div>
          ) : leaderboard.length === 0 ? (
            <p className="text-gray-600 dark:text-gray-400">No data available</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b dark:border-gray-700">
                    <th className="text-left py-3 px-4">Rank</th>
                    <th className="text-left py-3 px-4">Student</th>
                    <th className="text-left py-3 px-4">Accuracy</th>
                    <th className="text-left py-3 px-4">Questions</th>
                    <th className="text-left py-3 px-4">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {leaderboard.map((entry, idx) => (
                    <tr
                      key={idx}
                      className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition"
                    >
                      <td className="py-3 px-4">
                        <span className="font-bold text-lg">#{idx + 1}</span>
                      </td>
                      <td className="py-3 px-4 font-semibold">{entry.student_name}</td>
                      <td className="py-3 px-4">
                        {entry.total_questions > 0
                          ? `${Math.round((entry.correct_answers / entry.total_questions) * 100)}%`
                          : 'N/A'}
                      </td>
                      <td className="py-3 px-4">{entry.total_questions}</td>
                      <td className="py-3 px-4">
                        <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full text-sm font-semibold">
                          {entry.average_score.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {error && (
          <div className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

function StatBox({ icon, label, value, color }) {
  const colorClasses = {
    green: 'bg-green-50 dark:bg-green-900/20',
    blue: 'bg-blue-50 dark:bg-blue-900/20',
    purple: 'bg-purple-50 dark:bg-purple-900/20',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20',
  };

  return (
    <div className={`${colorClasses[color]} rounded-lg p-6`}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-gray-600 dark:text-gray-400">{label}</p>
        {icon}
      </div>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}

export default ProgressPage;
