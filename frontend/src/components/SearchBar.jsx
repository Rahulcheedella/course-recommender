import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Sparkles } from 'lucide-react';
import { recordInteraction } from '../services/api';

export default function SearchBar({ initialQuery = '', onSearch }) {
  const [query, setQuery] = useState(initialQuery);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    recordInteraction('search', null, { query: query.trim() });

    if (onSearch) {
      onSearch(query.trim());
    } else {
      navigate(`/explore?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ width: '100%', position: 'relative' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        background: 'rgba(30, 41, 59, 0.85)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(99, 102, 241, 0.3)',
        borderRadius: '16px',
        padding: '0.35rem 0.5rem 0.35rem 1.2rem',
        boxShadow: '0 8px 25px rgba(0, 0, 0, 0.25)',
        transition: 'var(--transition)'
      }}>
        <Search size={20} color="#818cf8" style={{ marginRight: '0.75rem', flexShrink: 0 }} />
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search technologies, skills, or engineering courses (e.g. React, ECE, Python, ANSYS)..."
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: '#f8fafc',
            fontSize: '1rem',
            padding: '0.6rem 0'
          }}
        />
        <button type="submit" className="btn btn-primary" style={{ borderRadius: '12px', padding: '0.6rem 1.25rem' }}>
          <Sparkles size={16} /> Search
        </button>
      </div>
    </form>
  );
}
