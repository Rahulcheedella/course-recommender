import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  BookOpen, 
  Compass, 
  Sparkles, 
  Network, 
  Heart, 
  User, 
  LogOut, 
  Map, 
  Search,
  CheckCircle2
} from 'lucide-react';
import { getActiveUserId } from '../services/api';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userJson = localStorage.getItem('user');
    if (userJson) {
      try {
        setUser(JSON.parse(userJson));
      } catch (e) {
        setUser(null);
      }
    } else {
      setUser(null);
    }
  }, [location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    navigate('/login');
  };

  return (
    <nav style={{
      background: 'rgba(15, 23, 42, 0.9)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '0.85rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Brand Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)'
          }}>
            <Network size={22} />
          </div>
          <div>
            <span style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '1.2rem',
              fontWeight: 800,
              background: 'linear-gradient(90deg, #ffffff, #a5b4fc)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              KnowledgeGraph
            </span>
            <span style={{
              display: 'block',
              fontSize: '0.7rem',
              color: 'var(--secondary)',
              fontWeight: 600,
              letterSpacing: '0.08em',
              textTransform: 'uppercase'
            }}>
              AI Learning Recommender
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <Link to="/" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            color: location.pathname === '/' ? '#818cf8' : 'var(--text-muted)',
            fontWeight: location.pathname === '/' ? 600 : 400,
            fontSize: '0.925rem',
            transition: 'var(--transition)'
          }}>
            <Sparkles size={18} /> Home
          </Link>

          <Link to="/explore" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            color: location.pathname === '/explore' ? '#818cf8' : 'var(--text-muted)',
            fontWeight: location.pathname === '/explore' ? 600 : 400,
            fontSize: '0.925rem'
          }}>
            <Compass size={18} /> Explore
          </Link>

          <Link to="/graph" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            color: location.pathname === '/graph' ? '#818cf8' : 'var(--text-muted)',
            fontWeight: location.pathname === '/graph' ? 600 : 400,
            fontSize: '0.925rem'
          }}>
            <Network size={18} /> Graph Viz
          </Link>

          <Link to="/learning-path" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            color: location.pathname === '/learning-path' ? '#818cf8' : 'var(--text-muted)',
            fontWeight: location.pathname === '/learning-path' ? 600 : 400,
            fontSize: '0.925rem'
          }}>
            <Map size={18} /> Learning Path
          </Link>

          {user && (
            <>
              <Link to="/my-learning" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                color: location.pathname === '/my-learning' ? '#818cf8' : 'var(--text-muted)',
                fontWeight: location.pathname === '/my-learning' ? 600 : 400,
                fontSize: '0.925rem'
              }}>
                <BookOpen size={18} /> My Learning
              </Link>

              <Link to="/wishlist" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                color: location.pathname === '/wishlist' ? '#818cf8' : 'var(--text-muted)',
                fontWeight: location.pathname === '/wishlist' ? 600 : 400,
                fontSize: '0.925rem'
              }}>
                <Heart size={18} /> Wishlist
              </Link>
            </>
          )}
        </div>

        {/* User Account Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Link to="/profile" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.4rem 0.8rem',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-color)',
                borderRadius: '20px'
              }}>
                <User size={16} color="#818cf8" />
                <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user.name}</span>
                <span className="badge badge-primary" style={{ fontSize: '0.65rem' }}>{user.department}</span>
              </Link>
              <button 
                onClick={handleLogout}
                className="btn btn-secondary" 
                style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
                title="Logout"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Link to="/login" className="btn btn-secondary" style={{ padding: '0.45rem 1rem', fontSize: '0.85rem' }}>
                Sign In
              </Link>
              <Link to="/register" className="btn btn-primary" style={{ padding: '0.45rem 1rem', fontSize: '0.85rem', backgroundColor: 'white' }}>
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
