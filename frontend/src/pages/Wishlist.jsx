import React, { useState, useEffect } from 'react';
import { Heart, BookOpen } from 'lucide-react';
import { fetchUserWishlist, getActiveUserId } from '../services/api';
import CourseCard from '../components/CourseCard';

export default function Wishlist() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const activeUserId = getActiveUserId();

  useEffect(() => {
    async function loadWishlist() {
      setLoading(true);
      try {
        const data = await fetchUserWishlist(activeUserId);
        setCourses(data || []);
      } catch (e) {
        console.error('Failed to load wishlist:', e);
      } finally {
        setLoading(false);
      }
    }
    loadWishlist();
  }, [activeUserId]);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: "steelblue", display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Heart size={28} color="#ef4444" fill="#ef4444" /> Saved Wishlist Courses
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Courses saved to your personal learning collection.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>Loading wishlist...</div>
      ) : courses.length > 0 ? (
        <div className="course-grid">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      ) : (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
          <h3>Your wishlist is currently empty</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Click the heart icon on any course card to save it for later.
          </p>
        </div>
      )}
    </div>
  );
}
