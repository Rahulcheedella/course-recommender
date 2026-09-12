import React, { useState, useEffect, useRef } from 'react';
import { Network, Sparkles, Filter, Info } from 'lucide-react';

export default function KnowledgeGraphVisualizer({ graphData }) {
  const [selectedNode, setSelectedNode] = useState(null);
  const canvasRef = useRef(null);

  const defaultNodes = [
    { id: 'u1', label: 'User Profile', group: 'User', x: 250, y: 200, color: '#6366f1', radius: 26 },
    { id: 'd1', label: 'Department: CSE', group: 'Department', x: 100, y: 100, color: '#06b6d4', radius: 20 },
    { id: 's1', label: 'Skill: Python', group: 'Skill', x: 100, y: 300, color: '#10b981', radius: 18 },
    { id: 's2', label: 'Skill: JavaScript', group: 'Skill', x: 220, y: 350, color: '#10b981', radius: 18 },
    { id: 't1', label: 'Tech: React', group: 'Technology', x: 400, y: 120, color: '#f59e0b', radius: 18 },
    { id: 't2', label: 'Tech: Machine Learning', group: 'Technology', x: 420, y: 280, color: '#f59e0b', radius: 18 },
    { id: 'c1', label: 'Course: React Complete Guide', group: 'Course', x: 550, y: 80, color: '#8b5cf6', radius: 22 },
    { id: 'c2', label: 'Course: ML with Python', group: 'Course', x: 580, y: 320, color: '#8b5cf6', radius: 22 }
  ];

  const defaultEdges = [
    { from: 'u1', to: 'd1', label: 'BELONGS_TO' },
    { from: 'u1', to: 's1', label: 'HAS_SKILL' },
    { from: 'u1', to: 's2', label: 'HAS_SKILL' },
    { from: 'u1', to: 't1', label: 'INTERESTED_IN' },
    { from: 's1', to: 't2', label: 'RELATED_TO' },
    { from: 't1', to: 'c1', label: 'COVERS' },
    { from: 's1', to: 'c2', label: 'TEACHES' },
    { from: 't2', to: 'c2', label: 'COVERS' }
  ];

  const nodes = (graphData && graphData.nodes && graphData.nodes.length > 0) ? graphData.nodes : defaultNodes;
  const edges = (graphData && graphData.edges && graphData.edges.length > 0) ? graphData.edges : defaultEdges;

  // Process nodes positions if not provided
  const processedNodes = nodes.map((n, index) => {
    if (n.x && n.y) return n;
    const angle = (index / nodes.length) * 2 * Math.PI;
    const distance = 140 + (index % 3) * 60;
    return {
      ...n,
      x: 350 + distance * Math.cos(angle),
      y: 220 + distance * Math.sin(angle),
      color: n.group === 'User' ? '#6366f1' : n.group === 'Department' ? '#06b6d4' : n.group === 'Skill' ? '#10b981' : n.group === 'Technology' ? '#f59e0b' : '#8b5cf6',
      radius: n.group === 'User' ? 24 : 18
    };
  });

  const nodeMap = new Map(processedNodes.map(n => [n.id, n]));

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Network size={22} color="#818cf8" /> Interactive Knowledge Graph Canvas
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            Traversing relationships: User → Department → Skills → Technologies → Courses
          </p>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.75rem', fontWeight: 600 }}>
          <span style={{ color: '#6366f1', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>● User</span>
          <span style={{ color: '#06b6d4', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>● Department</span>
          <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>● Skill</span>
          <span style={{ color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>● Technology</span>
          <span style={{ color: '#8b5cf6', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>● Course</span>
        </div>
      </div>

      {/* Interactive SVG Canvas */}
      <div style={{
        width: '100%',
        height: '420px',
        background: 'rgba(15, 23, 42, 0.95)',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <svg width="100%" height="100%" viewBox="0 0 700 440">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
            </marker>
          </defs>

          {/* Render Edges */}
          {edges.map((edge, idx) => {
            const source = nodeMap.get(edge.from);
            const target = nodeMap.get(edge.to);
            if (!source || !target) return null;

            const midX = (source.x + target.x) / 2;
            const midY = (source.y + target.y) / 2;

            return (
              <g key={idx}>
                <line
                  x1={source.x}
                  y1={source.y}
                  x2={target.x}
                  y2={target.y}
                  stroke="rgba(148, 163, 184, 0.3)"
                  strokeWidth="2"
                  markerEnd="url(#arrow)"
                />
                <text
                  x={midX}
                  y={midY - 4}
                  fill="#94a3b8"
                  fontSize="9"
                  textAnchor="middle"
                  fontWeight="600"
                >
                  {edge.label}
                </text>
              </g>
            );
          })}

          {/* Render Nodes */}
          {processedNodes.map((node) => {
            const isSelected = selectedNode && selectedNode.id === node.id;
            return (
              <g 
                key={node.id} 
                onClick={() => setSelectedNode(node)} 
                style={{ cursor: 'pointer' }}
              >
                {/* Halo for selected node */}
                {isSelected && (
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={node.radius + 8}
                    fill="none"
                    stroke="#818cf8"
                    strokeWidth="3"
                    strokeDasharray="4"
                  />
                )}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={node.radius}
                  fill={node.color}
                  filter="drop-shadow(0px 4px 10px rgba(0,0,0,0.5))"
                />
                <text
                  x={node.x}
                  y={node.y + node.radius + 14}
                  fill="#f8fafc"
                  fontSize="10"
                  fontWeight="700"
                  textAnchor="middle"
                >
                  {node.label.length > 20 ? node.label.substring(0, 18) + '...' : node.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected Node Details Overlay */}
        {selectedNode && (
          <div style={{
            position: 'absolute',
            bottom: '15px',
            left: '15px',
            background: 'rgba(30, 41, 59, 0.9)',
            border: '1px solid rgba(99, 102, 241, 0.4)',
            borderRadius: '12px',
            padding: '0.75rem 1rem',
            backdropFilter: 'blur(10px)',
            maxWidth: '280px'
          }}>
            <div style={{ fontSize: '0.75rem', color: '#818cf8', fontWeight: 600, textTransform: 'uppercase' }}>
              {selectedNode.group} Node Selected
            </div>
            <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'white', marginTop: '0.2rem' }}>
              {selectedNode.label}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
