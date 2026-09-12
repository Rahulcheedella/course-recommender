import React, { useState, useEffect } from 'react';
import { Network, Sparkles, Database, GitMerge, CheckCircle2 } from 'lucide-react';
import KnowledgeGraphVisualizer from '../components/KnowledgeGraphVisualizer';
import { fetchKnowledgeGraphData, getActiveUserId } from '../services/api';

export default function KnowledgeGraphPage() {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const activeUserId = getActiveUserId();

  useEffect(() => {
    async function loadGraph() {
      setLoading(true);
      try {
        const data = await fetchKnowledgeGraphData(activeUserId);
        setGraphData(data);
      } catch (e) {
        console.error('Failed to load knowledge graph data:', e);
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, [activeUserId]);

  return (
    <div style={{ maxWidth: '1050px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <div className="badge badge-primary" style={{ marginBottom: '0.5rem' }}>
          <Database size={12} style={{ marginRight: '0.3rem' }} /> Neo4j Graph Traversal Engine
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Network size={32} color="#818cf8" /> Knowledge Graph Exploration
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginTop: '0.25rem' }}>
          Visualize entity relationships connecting user departments, verified skills, technology interests, and course recommendations.
        </p>
      </div>

      {/* Visual Canvas Component */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
          Loading Neo4j sub-graph nodes and relationship edges...
        </div>
      ) : (
        <KnowledgeGraphVisualizer graphData={graphData} />
      )}

      {/* Research & Graph Explanation Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '2.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <GitMerge size={20} color="#06b6d4" /> Graph Traversal Logic
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.6' }}>
            Unlike flat relational databases, the Knowledge Graph executes Cypher queries traversing 2-hop and 3-hop paths:
          </p>
          <div style={{
            background: 'rgba(15, 23, 42, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '10px',
            padding: '0.85rem',
            marginTop: '0.75rem',
            fontFamily: 'monospace',
            fontSize: '0.825rem',
            color: '#a5b4fc',
            lineHeight: '1.6'
          }}>
            (User) ──[:INTERESTED_IN]──► (React)<br />
            (React) ──[:RELATED_TO]────► (JavaScript)<br />
            (JavaScript) ──[:RELATED_TO]► (Node.js)<br />
            (Course) ──[:COVERS]────────► (Node.js)<br />
            └──► Recommend Course with Explainable Trace
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={20} color="#f59e0b" /> Dynamic Weighting Engine
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.6' }}>
            Every interaction dynamically updates relationship weights:
          </p>
          <ul style={{ color: '#cbd5e1', fontSize: '0.85rem', marginTop: '0.5rem', paddingLeft: '1.25rem', lineHeight: '1.8' }}>
            <li><strong>Search Query:</strong> Weight +1.0</li>
            <li><strong>Course View / Click:</strong> Weight +2.0 to +2.5</li>
            <li><strong>Wishlist Save:</strong> Weight +4.0</li>
            <li><strong>Course Enrollment:</strong> Weight +6.0</li>
            <li><strong>Course Completion:</strong> Weight +8.0</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
