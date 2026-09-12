import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Clock, Users, Heart, Sparkles, ArrowRight } from 'lucide-react';
import { toggleWishlist, recordInteraction } from '../services/api';

export default function CourseCard({ course, showExplanation = true }) {
  const navigate = useNavigate();
  const [isWishlisted, setIsWishlisted] = useState(false);

  const handleCardClick = () => {
    recordInteraction('course_click', course.id);
    navigate(`/course/${course.id}`);
  };

  const handleWishlist = async (e) => {
    e.stopPropagation();
    const res = await toggleWishlist(course.id);
    setIsWishlisted(res.wishlisted);
  };

  return (
    <div 
      onClick={handleCardClick}
      className="glass-panel"
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
        cursor: 'pointer',
        transition: 'transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        position: 'relative'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)';
        e.currentTarget.style.boxShadow = '0 12px 25px rgba(0, 0, 0, 0.3)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Thumbnail Header */}
      <div style={{ position: 'relative', width: '100%', height: '160px', overflow: 'hidden' }}>
        <img 
          src={course.thumbnail || 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97'} 
          alt={course.title} 
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
        <div style={{
          position: 'absolute',
          top: '10px',
          left: '10px',
          display: 'flex',
          gap: '0.4rem'
        }}>
          <span className="badge badge-primary" style={{ backdropFilter: 'blur(8px)', background: 'rgba(15, 23, 42, 0.8)' }}>
            {course.department}
          </span>
          <span className="badge badge-secondary" style={{ backdropFilter: 'blur(8px)', background: 'rgba(15, 23, 42, 0.8)' }}>
            {course.difficulty}
          </span>
        </div>

        {/* Wishlist Button */}
        <button 
          onClick={handleWishlist}
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: 'rgba(15, 23, 42, 0.75)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: isWishlisted ? '#ef4444' : '#94a3b8',
            transition: 'var(--transition)'
          }}
          title="Save to Wishlist"
        >
          <Heart size={16} fill={isWishlisted ? '#ef4444' : 'none'} />
        </button>
      </div>

      {/* Card Content Body */}
      <div style={{ padding: '1.2rem', display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--secondary)', fontWeight: 600, marginBottom: '0.25rem' }}>
            {course.category}
          </div>
          <h3 style={{
            fontSize: '1.05rem',
            fontWeight: 700,
            lineHeight: '1.35',
            color: '#f8fafc',
            marginBottom: '0.4rem',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}>
            {course.title}
          </h3>
          <p style={{ fontSize: '0.825rem', color: '#94a3b8', marginBottom: '0.75rem' }}>
            {course.instructor}
          </p>
        </div>

        <div>
          {/* Metadata Metrics */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.8rem',
            color: '#cbd5e1',
            paddingBottom: '0.75rem',
            borderBottom: '1px solid rgba(255, 255, 255, 0.06)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#fbbf24', fontWeight: 600 }}>
              <Star size={14} fill="#fbbf24" />
              <span>{course.rating}</span>
              <span style={{ color: '#64748b', fontWeight: 400 }}>({(course.students / 1000).toFixed(1)}k)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#94a3b8' }}>
              <Clock size={14} />
              <span>{course.duration}</span>
            </div>
            <div style={{ fontWeight: 700, color: '#67e8f9' }}>
              ${course.price}
            </div>
          </div>

          {/* Explainable Recommendation Rationale Banner */}
          {showExplanation && course.recommendation_reason && (
            <div className="rec-explanation-banner">
              <Sparkles size={14} style={{ color: '#818cf8', flexShrink: 0 }} />
              <span style={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                {course.recommendation_reason}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
