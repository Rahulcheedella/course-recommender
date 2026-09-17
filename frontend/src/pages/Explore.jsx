import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Compass, Info } from 'lucide-react';
import SearchBar from '../components/SearchBar';
import Filters from '../components/Filters';
import CourseCard from '../components/CourseCard';
import { searchCourses } from '../services/api';

export default function Explore() {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [noResultsMessage, setNoResultsMessage] = useState(null);
  const [filters, setFilters] = useState({
    department: '',
    category: '',
    difficulty: '',
    min_rating: ''
  });

  const handleSearch = async (queryStr, currentFilters = filters) => {
    setLoading(true);
    setNoResultsMessage(null);
    try {
      const data = await searchCourses(queryStr, currentFilters);
      setCourses(data.results || []);
      if (data.no_results_message) {
        setNoResultsMessage(data.no_results_message);
      }
    } catch (e) {
      console.error('Failed to search courses:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch(initialQuery, filters);
  }, [initialQuery]);

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    handleSearch(initialQuery, newFilters);
  };

  const handleResetFilters = () => {
    const reset = { department: '', category: '', difficulty: '', min_rating: '' };
    setFilters(reset);
    handleSearch(initialQuery, reset);
  };


  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: "steelblue", marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Compass size={28} color="#818cf8" /> Explore Course Catalog
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Search and filter across Full Stack, AI/ML, ECE, EEE, Mechanical, Civil, Cybersecurity, and Cloud engineering domains.
        </p>

        <div style={{ marginTop: '1.25rem', maxWidth: '800px'}}>
          <SearchBar initialQuery={initialQuery} onSearch={(q) => handleSearch(q, filters)} />
        </div>
      </div>

      {/* Main Grid Layout: Sidebar Filters + Results */}
      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '1.75rem', alignItems: 'start' }}>
        <Filters 
          filters={filters}
          onChange={handleFilterChange}
          onReset={handleResetFilters}
        />

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              Found <strong style={{ color: 'white' }}>{courses.length}</strong> courses matching criteria
            </span>
          </div>

          {/* No-results / fallback message banner */}
          {noResultsMessage && (
            <div style={{
              display: 'flex', alignItems: 'flex-start', gap: '0.6rem',
              background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.3)',
              borderRadius: '10px', padding: '0.75rem 1rem', marginBottom: '1rem',
              fontSize: '0.85rem', color: '#a5b4fc'
            }}>
              <Info size={16} style={{ flexShrink: 0, marginTop: '1px', color: '#818cf8' }} />
              {noResultsMessage}
            </div>
          )}

          {loading ? (
            <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
              Searching courses...
            </div>
          ) : courses.length > 0 ? (
            <div className="course-grid">
              {courses.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
          ) : (
            <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <h3>No courses found matching your criteria</h3>
              <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                Try adjusting your search query or reset the sidebar filters.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
