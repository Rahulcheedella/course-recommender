import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Network, LogIn, Sparkles, UserCheck } from 'lucide-react';
import { loginUser } from '../services/api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await loginUser(email, password);
      localStorage.setItem('user', JSON.stringify(data.user));
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to sign in. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail) => {
    setEmail(demoEmail);
    setPassword('password123');
  };

  return (
    <div style={{
      maxWidth: '440px',
      margin: '4rem auto 0',
      padding: '0 1rem'
    }}>
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
            <Network size={32} />
          </div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'white' }}>
            Welcome Back
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Sign in to access personalized Knowledge Graph recommendations
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

        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label className="input-label">Email Address</label>
            <input 
              type="email"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. alex.cse@example.com"
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label">Password</label>
            <input 
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '0.8rem', marginTop: '0.5rem' }}
            disabled={loading}
          >
            <LogIn size={18} /> {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Users Preset Shortcuts */}
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.75rem', textAlign: 'center' }}>
            ⚡ Demo Test Accounts (Click to Autofill)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <button onClick={() => handleQuickLogin('alex.cse@example.com')} className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.4rem' }}>
              👨‍💻 CSE Student
            </button>
            <button onClick={() => handleQuickLogin('priya.ece@example.com')} className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.4rem' }}>
              ⚡ ECE Student
            </button>
            <button onClick={() => handleQuickLogin('david.mech@example.com')} className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.4rem' }}>
              ⚙️ Mech Student
            </button>
            <button onClick={() => handleQuickLogin('rohan.eee@example.com')} className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.4rem' }}>
              🔋 EEE Student
            </button>
          </div>
        </div>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: '#818cf8', fontWeight: 600 }}>
            Register Now
          </Link>
        </div>
      </div>
    </div>
  );
}
