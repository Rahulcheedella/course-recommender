import React from 'react';
import { Network } from 'lucide-react';
import CourseCard from './CourseCard';

export default function RecommendationSection({ title, subtitle, icon: Icon, courses = [], badge = null }) {
  if (!courses || courses.length === 0) return null;

  // Check if any course in this section has cross-department graph recommendations
  const hasCrossDept = courses.some(c =>
    c.recommendation_reason && c.recommendation_reason.toLowerCase().includes('cross-department')
  );

  return (
    <section style={{ marginBottom: '2.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem', flexWrap: 'wrap' }}>
        {Icon && <Icon size={22} style={{ color: '#818cf8' }} />}
        <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'black' }}>
          {title}
        </h2>
        {badge && (
          <span className="badge badge-primary" style={{ fontSize: '0.72rem' }}>
            {badge}
          </span>
        )}
        {hasCrossDept && (
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.2rem',
            fontSize: '0.7rem',
            padding: '0.15rem 0.6rem',
            borderRadius: '10px',
            background: 'rgba(6, 182, 212, 0.15)',
            border: '1px solid rgba(6, 182, 212, 0.4)',
            color: '#67e8f9'
          }}>
            <Network size={10} /> Cross-Domain Graph Match
          </span>
        )}
      </div>

      {subtitle && (
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          {subtitle}
        </p>
      )}

      <div className="course-grid">
        {courses.map((course) => (
          <CourseCard key={course.id} course={course} />
        ))}
      </div>
    </section>
  );
}
