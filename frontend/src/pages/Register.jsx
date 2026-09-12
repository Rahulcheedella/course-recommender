import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, Sparkles, Network, Check } from 'lucide-react';
import { registerUser } from '../services/api';

export default function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    department: 'CSE',
    experience: 'Beginner',
    skills: [],
    interests: []
  });
  const [skillInput, setSkillInput] = useState('');
  const [interestInput, setInterestInput] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const departments = ['CSE', 'IT', 'ECE', 'EEE', 'Mechanical', 'Civil', 'AI & DS', 'AI & ML', 'Mechatronics', 'Other'];
  const experienceLevels = ['Beginner', 'Intermediate', 'Advanced'];

  const handleAddSkill = () => {
    if (skillInput.trim() && !formData.skills.includes(skillInput.trim())) {
      setFormData((prev) => ({ ...prev, skills: [...prev.skills, skillInput.trim()] }));
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setFormData((prev) => ({ ...prev, skills: prev.skills.filter((s) => s !== skillToRemove) }));
  };

  const handleAddInterest = () => {
    if (interestInput.trim() && !formData.interests.includes(interestInput.trim())) {
      setFormData((prev) => ({ ...prev, interests: [...prev.interests, interestInput.trim()] }));
      setInterestInput('');
    }
  };

  const handleRemoveInterest = (interestToRemove) => {
    setFormData((prev) => ({ ...prev, interests: prev.interests.filter((i) => i !== interestToRemove) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await registerUser(formData);
      localStorage.setItem('user', JSON.stringify(data.user));
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please check input parameters.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '580px', margin: '2rem auto', padding: '0 1rem' }}>
      <div className="glass-panel" style={{ padding: '2.5rem 2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            marginBottom: '1rem',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
          }}>
            <UserPlus size={30} />
          </div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'white' }}>
            Create Learner Account
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Initialize your profile graph for personalized course discovery
          </p>
        </div>

        {error && (
          <div style={{
            padding: '0.75rem 1rem',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            color: '#fca5a5',
            fontSize: '0.85rem',
            marginBottom: '1.25rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="input-group">
              <label className="input-label">Full Name</label>
              <input 
                type="text"
                className="input-field"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Alex Chen"
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">Email Address</label>
              <input 
                type="email"
                className="input-field"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="alex@example.com"
                required
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="input-group">
              <label className="input-label">Department / Discipline</label>
              <select 
                className="input-field"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              >
                {departments.map((dept) => (
                  <option key={dept} value={dept} style={{ background: '#1e293b' }}>{dept}</option>
                ))}
              </select>
            </div>

            <div className="input-group">
              <label className="input-label">Experience Level</label>
              <select 
                className="input-field"
                value={formData.experience}
                onChange={(e) => setFormData({ ...formData, experience: e.target.value })}
              >
                {experienceLevels.map((lvl) => (
                  <option key={lvl} value={lvl} style={{ background: '#1e293b' }}>{lvl}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">Password</label>
            <input 
              type="password"
              className="input-field"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="••••••••"
              required
            />
          </div>

          {/* Skill Selection Tags */}
          <div className="input-group">
            <label className="input-label">Current Technical Skills</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input 
                type="text"
                className="input-field"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                placeholder="e.g. Python, C++, AutoCAD, MATLAB"
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddSkill(); } }}
              />
              <button type="button" onClick={handleAddSkill} className="btn btn-secondary">
                Add
              </button>
            </div>
            {formData.skills.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.6rem' }}>
                {formData.skills.map((s) => (
                  <span key={s} className="badge badge-primary" style={{ cursor: 'pointer' }} onClick={() => handleRemoveSkill(s)}>
                    {s} ✕
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Preferred Learning Domains */}
          <div className="input-group">
            <label className="input-label">Preferred Learning Domains / Interests</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input 
                type="text"
                className="input-field"
                value={interestInput}
                onChange={(e) => setInterestInput(e.target.value)}
                placeholder="e.g. React, Embedded Systems, GenAI, ANSYS"
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddInterest(); } }}
              />
              <button type="button" onClick={handleAddInterest} className="btn btn-secondary">
                Add
              </button>
            </div>
            {formData.interests.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.6rem' }}>
                {formData.interests.map((i) => (
                  <span key={i} className="badge badge-secondary" style={{ cursor: 'pointer' }} onClick={() => handleRemoveInterest(i)}>
                    {i} ✕
                  </span>
                ))}
              </div>
            )}
          </div>

          <button 
            type="submit" 
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '0.8rem', marginTop: '1rem' }}
            disabled={loading}
          >
            <Sparkles size={18} /> {loading ? 'Initializing Knowledge Graph...' : 'Create Account & Discover Courses'}
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#818cf8', fontWeight: 600 }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
