import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Star, Clock, Users, Heart, BookOpen, CheckCircle, Sparkles, Network, ArrowLeft } from 'lucide-react';
import { fetchCourseDetails, enrollCourse, toggleWishlist, markCourseCompleted } from '../services/api';
import CourseCard from '../components/CourseCard';

export default function CourseDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrolled, setEnrolled] = useState(false);
  const [wishlisted, setWishlisted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const data = await fetchCourseDetails(id);
        setCourse(data.course);
        setRelated(data.related_courses || []);
      } catch (e) {
        console.error('Failed to load course details:', e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  const handleEnroll = async () => {
    const res = await enrollCourse(id);
    if (res.enrolled) {
      setEnrolled(true);
      setMsg('🎉 Successfully enrolled in this course!');
    }
  };

  const handleWishlist = async () => {
    const res = await toggleWishlist(id);
    setWishlisted(res.wishlisted);
    setMsg(res.wishlisted ? '❤️ Added to your wishlist' : 'Removed from wishlist');
  };

  const handleComplete = async () => {
    const res = await markCourseCompleted(id);
    if (res.completed) {
      setCompleted(true);
      setMsg('🏆 Course marked as completed! Knowledge Graph updated.');
    }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>Loading course metadata...</div>;
  if (!course) return <div style={{ textAlign: 'center', padding: '4rem 0' }}>Course not found.</div>;

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <button 
        onClick={() => navigate(-1)} 
        style={{ background: 'none', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '1.25rem', fontSize: '0.9rem' }}
      >
        <ArrowLeft size={16} /> Back to Courses
      </button>

      {msg && (
        <div style={{
          padding: '0.75rem 1rem',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: '8px',
          color: '#6ee7b7',
          fontSize: '0.9rem',
          marginBottom: '1.5rem'
        }}>
          {msg}
        </div>
      )}

      {/* Main Course Hero Panel */}
      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem', alignItems: 'start' }}>
          <div>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <span className="badge badge-primary">{course.department}</span>
              <span className="badge badge-secondary">{course.category}</span>
              <span className="badge badge-accent">{course.difficulty}</span>
            </div>

            <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'white', marginBottom: '0.75rem', lineHeight: '1.3' }}>
              {course.title}
            </h1>

            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '1rem' }}>
              Created by <strong style={{ color: '#f8fafc' }}>{course.instructor}</strong>
            </p>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#fbbf24', fontWeight: 700 }}>
                <Star size={18} fill="#fbbf24" /> {course.rating} ★
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Users size={16} /> {(course.students / 1000).toFixed(1)}k Students
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Clock size={16} /> {course.duration}
              </div>
            </div>

            {/* Recommendation Explanation Banner */}
            {course.recommendation_reason && (
              <div className="rec-explanation-banner" style={{ fontSize: '0.875rem', padding: '0.75rem 1rem' }}>
                <Sparkles size={18} style={{ color: '#818cf8', flexShrink: 0 }} />
                <span>
                  <strong>Knowledge Graph Rationale:</strong> {course.recommendation_reason}
                </span>
              </div>
            )}
          </div>

          {/* Action Box Card */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '1.25rem',
            textAlign: 'center'
          }}>
            <img 
              src={course.thumbnail} 
              alt={course.title} 
              style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '10px', marginBottom: '1rem' }} 
            />

            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#67e8f9', marginBottom: '1rem' }}>
              ${course.price}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <button 
                onClick={handleEnroll} 
                className="btn btn-primary" 
                style={{ justifyContent: 'center', width: '100%', padding: '0.75rem' }}
              >
                <BookOpen size={18} /> {enrolled ? 'Enrolled ✓' : 'Enroll Now'}
              </button>

              <button 
                onClick={handleWishlist} 
                className="btn btn-secondary" 
                style={{ justifyContent: 'center', width: '100%', padding: '0.75rem' }}
              >
                <Heart size={18} fill={wishlisted ? '#ef4444' : 'none'} color={wishlisted ? '#ef4444' : 'white'} /> 
                {wishlisted ? 'Saved in Wishlist' : 'Add to Wishlist'}
              </button>

              <button 
                onClick={handleComplete} 
                className="btn btn-outline" 
                style={{ justifyContent: 'center', width: '100%', padding: '0.6rem', fontSize: '0.85rem' }}
              >
                <CheckCircle size={16} /> {completed ? 'Completed ✓' : 'Mark Completed'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Course Description & Skills */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white', marginBottom: '0.75rem' }}>
            Course Overview & Description
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.925rem', lineHeight: '1.6' }}>
            {course.description}
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white', marginBottom: '0.75rem' }}>
            Skills & Technologies Covered
          </h3>
          <div style={{ marginBottom: '1rem' }}>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8', display: 'block', marginBottom: '0.4rem' }}>Skills Taught:</span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {course.skills?.map((s) => (
                <span key={s} className="badge badge-primary">{s}</span>
              ))}
            </div>
          </div>

          <div>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8', display: 'block', marginBottom: '0.4rem' }}>Technologies:</span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {course.technologies?.map((t) => (
                <span key={t} className="badge badge-secondary">{t}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Graph Connected Related Courses */}
      {related.length > 0 && (
        <section style={{ marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'white', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Network size={22} color="#818cf8" /> Knowledge Graph Connected Courses
          </h2>
          <div className="course-grid">
            {related.map((c) => (
              <CourseCard key={c.id} course={c} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
