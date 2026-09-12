import React, { useState, useEffect, useCallback } from 'react';
import {
  Sparkles, Compass, BookOpen, Activity, Flame, GraduationCap,
  Network, RefreshCw, ArrowRight, Brain, History, Clock
} from 'lucide-react';
import SearchBar from '../components/SearchBar';
import RecommendationSection from '../components/RecommendationSection';
import { fetchRecommendations, fetchUserInterests, getActiveUserId } from '../services/api';

export default function Home() {
  const [recs, setRecs] = useState(null);
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const activeUserId = getActiveUserId();

  useEffect(() => {
    try {
      const stored = localStorage.getItem('user');
      if (stored) setUserProfile(JSON.parse(stored));
    } catch (_) {}
  }, []);

  const loadDashboardData = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    else setLoading(true);
    try {
      const [recsData, interestsData] = await Promise.all([
        fetchRecommendations(activeUserId),
        fetchUserInterests(activeUserId)
      ]);
      setRecs(recsData);
      setInterests(interestsData);
    } catch (e) {
      console.error('Failed to load dashboard:', e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [activeUserId]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Cross-domain insight for non-CS students with tech interests
  const getCrossDomainMessage = () => {
    if (!userProfile) return null;
    const dept = userProfile.department || '';
    const nonCsDepts = ['Mechanical', 'Civil', 'EEE', 'ECE', 'Mechatronics', 'ACSC', 'Aeronautical'];
    const isCross = nonCsDepts.some(d => dept.includes(d));
    if (!isCross) return null;
    const techInterests = (userProfile.interests || []).filter(i =>
      ['python', 'ml', 'ai', 'react', 'java', 'data', 'cloud', 'programming'].some(k => i.toLowerCase().includes(k))
    );
    if (techInterests.length === 0 && interests.length === 0) return null;
    const topInterest = techInterests[0] || (interests[0]?.topic) || 'technology';
    return { dept, interest: topInterest };
  };

  const crossDomain = getCrossDomainMessage();

  return (
    <div>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '3rem 1rem 2rem' }}>
        <div className="badge badge-primary" style={{ marginBottom: '1rem', padding: '0.4rem 1rem', fontSize: '0.8rem' }}>
          <Sparkles size={14} style={{ marginRight: '0.4rem' }} />
          Knowledge Graph Personalization Active
        </div>

        <h1 style={{
          fontSize: '2.5rem', fontWeight: 800, lineHeight: '1.2', marginBottom: '1rem',
          background: 'linear-gradient(135deg, #ffffff, #a5b4fc, #67e8f9)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
        }}>
          AI-Powered Course Discovery<br />& Personalized Recommendations
        </h1>

        <p style={{ maxWidth: '680px', margin: '0 auto 2rem', color: 'var(--text-muted)', fontSize: '1.05rem', lineHeight: '1.6' }}>
          Discover courses tailored to your department, technical skills, and evolving learning interest graph.
        </p>

        <div style={{ maxWidth: '750px', margin: '0 auto 1rem' }}>
          <SearchBar />
        </div>

        {activeUserId && (
          <button
            onClick={() => loadDashboardData(true)}
            disabled={refreshing}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
              padding: '0.45rem 1.1rem', background: 'rgba(99, 102, 241, 0.12)',
              border: '1px solid rgba(99, 102, 241, 0.35)', borderRadius: '20px',
              color: '#a5b4fc', fontSize: '0.8rem', cursor: 'pointer',
              transition: 'all 0.2s ease', opacity: refreshing ? 0.6 : 1
            }}
          >
            <RefreshCw size={14} style={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
            {refreshing ? 'Refreshing Graph...' : 'Refresh Recommendations'}
          </button>
        )}
      </section>

      {/* Cross-Domain Network Alert */}
      {crossDomain && (
        <div className="glass-panel" style={{
          padding: '1.2rem 1.5rem', marginBottom: '2rem',
          borderLeft: '3px solid #818cf8', background: 'rgba(99, 102, 241, 0.08)'
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
            <Network size={22} color="#818cf8" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'white' }}>
                  Cross-Domain Learning Network Detected
                </h4>
                <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>Graph-Powered</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.5', marginBottom: '0.5rem' }}>
                As a <strong style={{ color: 'white' }}>{crossDomain.dept}</strong> student interested
                in <strong style={{ color: '#818cf8' }}>{crossDomain.interest}</strong>, we've mapped
                cross-domain courses bridging your engineering background with CS/tech skills.
              </p>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.75rem', color: '#818cf8' }}>
                  <Brain size={12} style={{ marginRight: '0.25rem', verticalAlign: 'middle' }} />
                  Neo4j 2-hop graph traversal active
                </span>
                <span style={{ fontSize: '0.75rem', color: '#67e8f9' }}>
                  <ArrowRight size={12} style={{ marginRight: '0.25rem', verticalAlign: 'middle' }} />
                  {crossDomain.dept} → {crossDomain.interest} → Related Courses
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Interest Profile Bars */}
      {interests.length > 0 && (
        <section className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Activity size={20} color="#818cf8" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'white' }}>
                Your Knowledge Graph Interest Profile
              </h3>
            </div>
            {userProfile?.department && (
              <span className="badge badge-secondary" style={{ fontSize: '0.75rem' }}>
                {userProfile.department} Student
              </span>
            )}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.85rem' }}>
            {interests.map((item, idx) => (
              <div key={idx} style={{
                background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1rem',
                borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.4rem' }}>
                  <span>{item.topic}</span>
                  <span style={{ color: '#818cf8' }}>{item.score}%</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${item.score}%`, height: '100%',
                    background: 'linear-gradient(90deg, #6366f1, #06b6d4)',
                    borderRadius: '3px', transition: 'width 0.8s ease'
                  }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
          <Sparkles size={32} color="#6366f1" style={{ margin: '0 auto 0.75rem', display: 'block', animation: 'pulse 1.5s ease-in-out infinite' }} />
          Loading personalized Knowledge Graph recommendations...
        </div>
      ) : recs ? (
        <>
          {/* Continue Learning */}
          {recs.continue_learning?.length > 0 && (
            <RecommendationSection
              title="Continue Learning"
              subtitle="Pick up where you left off"
              icon={BookOpen}
              courses={recs.continue_learning}
            />
          )}

          {/* Based on Your Recent History */}
          {recs.based_on_history?.length > 0 && (
            <section style={{ marginBottom: '2.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
                <History size={22} style={{ color: '#f59e0b' }} />
                <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'black' }}>
                  Based on Your Recent Activity
                </h2>
                <span style={{
                  fontSize: '0.7rem', padding: '0.15rem 0.6rem', borderRadius: '10px',
                  background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.4)',
                  color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '0.2rem'
                }}>
                  <Clock size={10} /> From your interaction history
                </span>
              </div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                Courses matched to your recent searches, clicks, and chatbot queries
              </p>
              <div className="course-grid">
                {recs.based_on_history.map((course) => (
                  <div
                    key={course.id}
                    onClick={() => window.location.href = `/course/${course.id}`}
                    className="glass-panel"
                    style={{ cursor: 'pointer', transition: 'transform 0.2s ease' }}
                    onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.borderColor = 'rgba(245,158,11,0.4)'; }}
                    onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'; }}
                  >
                    <div style={{ position: 'relative', height: '140px', overflow: 'hidden' }}>
                      <img src={course.thumbnail || 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97'} alt=""
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        onError={e => { e.target.src = 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97'; }}
                      />
                      <div style={{ position: 'absolute', top: 8, left: 8, display: 'flex', gap: '0.3rem' }}>
                        <span className="badge badge-primary" style={{ backdropFilter: 'blur(8px)', background: 'rgba(15,23,42,0.85)' }}>{course.department}</span>
                      </div>
                    </div>
                    <div style={{ padding: '1rem' }}>
                      <div style={{ fontSize: '0.75rem', color: '#f59e0b', fontWeight: 600, marginBottom: '0.25rem' }}>{course.category}</div>
                      <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.3rem',
                        overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box',
                        WebkitLineClamp: 2, WebkitBoxOrient: 'vertical'
                      }}>{course.title}</h3>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                        ★ {course.rating} · {course.difficulty} · ${course.price}
                      </div>
                      {course.recommendation_reason && (
                        <div style={{ marginTop: '0.5rem', fontSize: '0.7rem', color: '#f59e0b',
                          display: 'flex', alignItems: 'center', gap: '0.25rem'
                        }}>
                          <History size={10} /> {course.recommendation_reason}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Recommended For You */}
          <RecommendationSection
            title="Recommended For You"
            subtitle="Curated by Knowledge Graph multi-hop skill matching"
            icon={Sparkles}
            courses={recs.recommended_for_you}
          />

          {/* Popular in Department */}
          <RecommendationSection
            title="Popular in Your Department"
            subtitle="Top picks for your engineering track"
            icon={GraduationCap}
            courses={recs.popular_in_department}
          />

          {/* Because You Viewed */}
          <RecommendationSection
            title="Because You Browsed"
            subtitle="Connected to your recent tech exploration graph"
            icon={Compass}
            courses={recs.because_you_viewed}
          />

          {/* Trending */}
          <RecommendationSection
            title="Trending Across All Domains"
            subtitle="Highest rated courses across all engineering & tech domains"
            icon={Flame}
            courses={recs.trending_courses}
          />
        </>
      ) : null}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
      `}</style>
    </div>
  );
}
