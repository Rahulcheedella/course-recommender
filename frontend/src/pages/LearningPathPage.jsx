import React, { useState, useEffect } from 'react';
import { Map, ArrowDown, Sparkles, CheckCircle2, ChevronRight } from 'lucide-react';
import { fetchLearningPath, getActiveUserId } from '../services/api';
import CourseCard from '../components/CourseCard';

export default function LearningPathPage() {
  const [role, setRole] = useState('AI Engineer');
  const [pathData, setPathData] = useState(null);
  const [loading, setLoading] = useState(true);
  const activeUserId = getActiveUserId();

  const roles = [
    'AI Engineer',
    'Full Stack Developer',
    'ECE Embedded Engineer',
    'Mechanical Design Specialist',
    'Civil BIM & Structural Specialist'
  ];

  useEffect(() => {
    async function loadPath() {
      setLoading(true);
      try {
        const data = await fetchLearningPath(activeUserId, role);
        setPathData(data);
      } catch (e) {
        console.error('Failed to load learning path:', e);
      } finally {
        setLoading(false);
      }
    }
    loadPath();
  }, [role, activeUserId]);

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <div className="badge badge-primary" style={{ marginBottom: '0.5rem' }}>
          <Sparkles size={12} style={{ marginRight: '0.3rem' }} /> Knowledge Graph Skill Tree Generator
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'white' }}>
          Structured Career Learning Paths
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginTop: '0.25rem' }}>
          Step-by-step milestone roadmaps generated from course prerequisite graph relationships.
        </p>

        {/* Role Selector Buttons */}
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem' }}>
          {roles.map((r) => (
            <button
              key={r}
              onClick={() => setRole(r)}
              className={role === r ? 'btn btn-primary' : 'btn btn-secondary'}
              style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>Generating learning path steps...</div>
      ) : pathData && pathData.steps ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'relative' }}>
          {pathData.steps.map((step, idx) => (
            <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div 
                className="glass-panel" 
                style={{
                  width: '100%',
                  padding: '1.5rem',
                  display: 'grid',
                  gridTemplateColumns: '120px 1fr 280px',
                  gap: '1.5rem',
                  alignItems: 'center',
                  borderLeft: '4px solid #6366f1'
                }}
              >
                <div>
                  <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>Step {step.step}</span>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: 'white', marginTop: '0.3rem' }}>
                    {step.title}
                  </h4>
                </div>

                <div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.25rem' }}>
                    {step.name}
                  </div>
                  <p style={{ fontSize: '0.825rem', color: '#94a3b8' }}>
                    {step.course_details?.description || 'Prerequisite milestone in this skill roadmap.'}
                  </p>
                  <div style={{ display: 'flex', gap: '0.3rem', marginTop: '0.5rem' }}>
                    {step.course_details?.skills?.slice(0, 3).map((s) => (
                      <span key={s} className="badge badge-secondary" style={{ fontSize: '0.65rem' }}>{s}</span>
                    ))}
                  </div>
                </div>

                {step.course_details ? (
                  <CourseCard course={step.course_details} showExplanation={false} />
                ) : (
                  <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    Course Node Linked
                  </div>
                )}
              </div>

              {/* Arrow Indicator for Next Step */}
              {idx < pathData.steps.length - 1 && (
                <div style={{ margin: '0.75rem 0', color: '#818cf8' }}>
                  <ArrowDown size={24} />
                </div>
              )}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
