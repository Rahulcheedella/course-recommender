import React, { useState, useEffect } from 'react';
import { User, Activity, History, BookOpen, Heart, Award, GraduationCap } from 'lucide-react';
import { fetchUserProfile, fetchUserInterests, fetchUserEnrollments, fetchUserWishlist, getActiveUserId } from '../services/api';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [interests, setInterests] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const activeUserId = getActiveUserId();

  useEffect(() => {
    async function loadProfileData() {
      setLoading(true);
      try {
        const [prof, intData, enrData, wishData] = await Promise.all([
          fetchUserProfile(activeUserId),
          fetchUserInterests(activeUserId),
          fetchUserEnrollments(activeUserId),
          fetchUserWishlist(activeUserId)
        ]);
        setProfile(prof);
        setInterests(intData);
        setEnrollments(enrData);
        setWishlist(wishData);
      } catch (e) {
        console.error('Failed to load profile data:', e);
      } finally {
        setLoading(false);
      }
    }
    loadProfileData();
  }, [activeUserId]);

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>Loading user profile...</div>;
  if (!profile) return <div style={{ textAlign: 'center', padding: '4rem 0' }}>Please log in to view your profile.</div>;

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Profile Header */}
      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <div style={{
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
        }}>
          <User size={36} />
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'white' }}>{profile.name}</h1>
            <span className="badge badge-primary">{profile.department} Department</span>
            <span className="badge badge-secondary">{profile.experience}</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{profile.email}</p>
        </div>
      </div>

      {/* Stats Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem', marginBottom: '2rem' }}>
        <div className="glass-panel" style={{ padding: '1.25rem', textAlign: 'center' }}>
          <BookOpen size={24} color="#818cf8" style={{ marginBottom: '0.5rem' }} />
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white' }}>{enrollments.length}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Active Courses</div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem', textAlign: 'center' }}>
          <Heart size={24} color="#ef4444" style={{ marginBottom: '0.5rem' }} />
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white' }}>{wishlist.length}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Saved Wishlist</div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem', textAlign: 'center' }}>
          <Award size={24} color="#10b981" style={{ marginBottom: '0.5rem' }} />
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white' }}>
            {enrollments.filter(e => e.enrollment_status === 'completed').length}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Completed Courses</div>
        </div>
      </div>

      {/* Skills & Graph Interest Profile */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <GraduationCap size={20} color="#818cf8" /> Verified Technical Skills
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {profile.skills && profile.skills.length > 0 ? (
              profile.skills.map((s) => (
                <span key={s} className="badge badge-primary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>{s}</span>
              ))
            ) : (
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No skills listed yet.</span>
            )}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={20} color="#06b6d4" /> Graph Interest Profile
          </h3>
          {interests.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {interests.map((item, idx) => (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, color: 'white', marginBottom: '0.2rem' }}>
                    <span>{item.topic}</span>
                    <span style={{ color: '#67e8f9' }}>{item.score}%</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', background: '#334155', borderRadius: '3px' }}>
                    <div style={{ width: `${item.score}%`, height: '100%', background: 'linear-gradient(90deg, #06b6d4, #6366f1)', borderRadius: '3px' }} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No dynamic interest graph data yet. Explore or search courses!</span>
          )}
        </div>
      </div>
    </div>
  );
}
