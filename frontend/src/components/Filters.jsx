import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';

export default function Filters({ filters, onChange, onReset }) {
  const departments = ['All', 'CSE', 'ECE', 'EEE', 'Mechanical', 'Civil', 'AI & DS', 'AI & ML', 'Mechatronics'];
  const categories = [
    'All', 'Full Stack Development', 'Frontend Development', 'Backend Development',
    'Data Structures & Algorithms', 'Artificial Intelligence', 'Machine Learning', 
    'Deep Learning', 'Generative AI', 'Cloud Computing', 'Cyber Security',
    'Mechanical Engineering', 'EEE', 'ECE', 'VLSI', 'Embedded Systems', 
    'Civil Engineering', 'CAD/BIM', 'Robotics', 'Automation'
  ];
  const difficulties = ['All', 'Beginner', 'Intermediate', 'Advanced'];

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', height: 'fit-content' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.2rem', paddingBottom: '0.6rem', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, fontSize: '1.05rem' }}>
          <Filter size={18} color="#818cf8" /> Filter Courses
        </div>
        <button 
          onClick={onReset} 
          style={{ background: 'none', color: 'var(--text-muted)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
        >
          <RotateCcw size={14} /> Reset
        </button>
      </div>

      {/* Department Filter */}
      <div className="input-group">
        <label className="input-label">Department</label>
        <select 
          className="input-field" 
          value={filters.department || 'All'} 
          onChange={(e) => onChange('department', e.target.value === 'All' ? '' : e.target.value)}
        >
          {departments.map((dept) => (
            <option key={dept} value={dept} style={{ background: 'white' }}>{dept}</option>
          ))}
        </select>
      </div>

      {/* Domain Category Filter */}
      <div className="input-group">
        <label className="input-label">Category / Domain</label>
        <select 
          className="input-field" 
          value={filters.category || 'All'} 
          onChange={(e) => onChange('category', e.target.value === 'All' ? '' : e.target.value)}
        >
          {categories.map((cat) => (
            <option key={cat} value={cat} style={{ background: 'white' }}>{cat}</option>
          ))}
        </select>
      </div>

      {/* Difficulty Filter */}
      <div className="input-group">
        <label className="input-label">Difficulty Level</label>
        <select 
          className="input-field" 
          value={filters.difficulty || 'All'} 
          onChange={(e) => onChange('difficulty', e.target.value === 'All' ? '' : e.target.value)}
        >
          {difficulties.map((diff) => (
            <option key={diff} value={diff} style={{ background: 'white' }}>{diff}</option>
          ))}
        </select>
      </div>

      {/* Min Rating Filter */}
      <div className="input-group">
        <label className="input-label">Minimum Rating</label>
        <select 
          className="input-field" 
          value={filters.min_rating || 'All'} 
          onChange={(e) => onChange('min_rating', e.target.value === 'All' ? '' : e.target.value)}
        >
          <option value="All" style={{ background: 'white' }}>Any Rating</option>
          <option value="4.8" style={{ background: 'white' }}>4.8 ★ & above</option>
          <option value="4.5" style={{ background: 'white' }}>4.5 ★ & above</option>
          <option value="4.0" style={{ background: 'white' }}>4.0 ★ & above</option>
        </select>
      </div>
    </div>
  );
}
