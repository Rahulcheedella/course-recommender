import React, { useState, useEffect } from 'react';
import { BookOpen, CheckCircle2 } from 'lucide-react';
import { fetchUserEnrollments, getActiveUserId } from '../services/api';
import CourseCard from '../components/CourseCard';

export default function MyLearning() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const activeUserId = getActiveUserId();

  useEffect(() => {
    async function loadEnrollments() {
      setLoading(true);
      try {
        const data = await fetchUserEnrollments(activeUserId);
        setCourses(data || []);
      } catch (e) {
        console.error('Failed to load enrollments:', e);
      } finally {
        setLoading(false);
      }
    }
    loadEnrollments();
  }, [activeUserId]);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <BookOpen size={28} color="#818cf8" /> My Active Enrollments
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Track active course progress and completion milestones.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>Loading enrolled courses...</div>
      ) : courses.length > 0 ? (
        <div className="course-grid">
          {courses.map((course) => (
            <div key={course.id} style={{ position: 'relative' }}>
              <CourseCard course={course} />
              <div style={{
                position: 'absolute',
                bottom: '10px',
                left: '10px',
                right: '10px',
                background: 'rgba(15, 23, 42, 0.9)',
                padding: '0.4rem 0.6rem',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.75rem',
                zIndex: 2
              }}>
                <span style={{ color: course.enrollment_status === 'completed' ? '#10b981' : '#67e8f9', fontWeight: 700 }}>
                  {course.enrollment_status === 'completed' ? '✓ Completed' : 'In Progress'}
                </span>
                <span style={{ color: '#94a3b8' }}>{course.progress}% Completed</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
          <h3>No active course enrollments</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Explore recommendations and click "Enroll Now" to start learning.
          </p>
        </div>
      )}
    </div>
  );
}
