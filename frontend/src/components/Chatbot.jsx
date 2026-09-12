import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  X,
  Send,
  Sparkles,
  BookOpen,
  Tag,
  Network,
  Brain,
  Code2,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { sendChatMessage } from '../services/api';

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);

  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: "Hello! I am your AI Learning Assistant powered by Neo4j Knowledge Graph + Llama 1B. Ask me what to learn, explore career paths, or get course recommendations based on your department and interests!",
      courses: [],
      entities: null
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const suggestedPrompts = [
    "I am an ECE student, what should I learn?",
    "What courses suit an ACSC student?",
    "Show me embedded systems courses",
    "Suggest VLSI and FPGA courses",
    "I want to learn Python for engineering",
    "What DSP courses are available?",
    "Best courses for IoT development",
    "Recommend Signal Processing courses"
  ];

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({
          behavior: 'smooth'
        });
      }, 80);
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim();

    if (!query || loading) return;

    setMessages(prev => [
      ...prev,
      {
        sender: 'user',
        text: query
      }
    ]);

    if (!textToSend) {
      setInput('');
    }

    setLoading(true);

    try {
      const res = await sendChatMessage(query);

      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: res.reply,
          courses: res.recommended_courses || [],
          entities: res.entities || [],
          matched_techs: res.matched_techs || [],
          graph_hops: res.graph_hops || [],
          cypher_queries: res.cypher_queries || [],
          neo4j_available: res.neo4j_available !== false
        }
      ]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: "Unable to reach the Knowledge Graph engine. Please ensure the backend is running.",
          courses: [],
          entities: null
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '25px',
        right: '25px',
        zIndex: 1000
      }}
    >
      {/* Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 25px rgba(99, 102, 241, 0.5)',
            border: '2px solid rgba(255, 255, 255, 0.2)',
            transition:
              'transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
            cursor: 'pointer'
          }}
          onMouseEnter={e => {
            e.currentTarget.style.transform = 'scale(1.1)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
          title="Open AI Learning Assistant"
        >
          <Bot size={28} />
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div
          className="glass-panel"
          style={{
            width: '420px',
            maxHeight: '640px',
            height: '84vh',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
            border: '1px solid rgba(99, 102, 241, 0.4)',
            overflow: 'hidden',
            borderRadius: '20px'
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '1rem 1.25rem',
              background:
                'linear-gradient(90deg, #1e1b4b, #312e81)',
              borderBottom:
                '1px solid rgba(255, 255, 255, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem'
              }}
            >
              <div
                style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '50%',
                  background: '#6366f1',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Bot size={20} color="white" />
              </div>

              <div>
                {/* AI Learning Assistant - WHITE */}
                <h4
                  style={{
                    fontSize: '0.95rem',
                    fontWeight: 700,
                    color: '#ffffff'
                  }}
                >
                  AI Learning Assistant
                </h4>

                <span
                  style={{
                    fontSize: '0.68rem',
                    color: '#a5b4fc',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem'
                  }}
                >
                  <Network size={10} />
                  GraphRAG · Cypher → Neo4j → Llama 1B
                </span>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                padding: '0.2rem'
              }}
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              padding: '1rem',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.9rem'
            }}
          >
            {messages.map((msg, idx) => (
              <ChatMessage
                key={idx}
                msg={msg}
              />
            ))}

            {loading && (
              <div
                style={{
                  alignSelf: 'flex-start',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.4rem'
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#94a3b8',
                    fontSize: '0.8rem'
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      gap: '3px'
                    }}
                  >
                    {[0, 1, 2].map(i => (
                      <div
                        key={i}
                        style={{
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          background: '#818cf8',
                          animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`
                        }}
                      />
                    ))}
                  </div>

                  <span
                    style={{
                      fontStyle: 'italic',
                      fontSize: '0.78rem'
                    }}
                  >
                    Running GraphRAG Pipeline…
                  </span>
                </div>

                <PipelineStepIndicator />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Prompts */}
          <div
            style={{
              padding: '0.5rem 0.75rem',
              background: 'rgba(15, 23, 42, 0.95)',
              borderTop:
                '1px solid rgba(255, 255, 255, 0.05)',
              display: 'flex',
              gap: '0.4rem',
              overflowX: 'auto',
              whiteSpace: 'nowrap'
            }}
          >
            {suggestedPrompts.map((p, i) => (
              <button
                key={i}
                onClick={() => handleSend(p)}
                style={{
                  fontSize: '0.68rem',
                  padding: '0.25rem 0.6rem',
                  borderRadius: '12px',
                  background:
                    'rgba(99, 102, 241, 0.13)',
                  color: '#a5b4fc',
                  border:
                    '1px solid rgba(99, 102, 241, 0.28)',
                  flexShrink: 0,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background =
                    'rgba(99,102,241,0.28)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background =
                    'rgba(99,102,241,0.13)';
                }}
              >
                {p}
              </button>
            ))}
          </div>

          {/* Input */}
          <div
            style={{
              padding: '0.75rem',
              background: '#0f172a',
              borderTop:
                '1px solid rgba(255,255,255,0.08)',
              display: 'flex',
              gap: '0.5rem'
            }}
          >
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e =>
                e.key === 'Enter' &&
                !e.shiftKey &&
                handleSend()
              }
              placeholder="Ask about courses, career paths, ECE/CSE/Mech…"
              style={{
                flex: 1,
                background:
                  'rgba(30,41,59,0.8)',
                border:
                  '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                padding: '0.5rem 0.85rem',
                color: 'white',
                fontSize: '0.875rem',
                outline: 'none'
              }}
              onFocus={e => {
                e.target.style.borderColor =
                  'rgba(99,102,241,0.6)';
              }}
              onBlur={e => {
                e.target.style.borderColor =
                  'rgba(255,255,255,0.1)';
              }}
            />

            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="btn btn-primary"
              style={{
                borderRadius: '12px',
                padding: '0.5rem 0.85rem',
                opacity:
                  loading || !input.trim()
                    ? 0.5
                    : 1
              }}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      )}

      <style>{`
        @keyframes bounce {
          0%, 60%, 100% {
            transform: translateY(0);
          }

          30% {
            transform: translateY(-6px);
          }
        }
      `}</style>
    </div>
  );
}

/* ── Sub-component: Pipeline Steps Indicator ─────────────────────────── */
function PipelineStepIndicator() {
  const steps = [
    {
      label: 'Step 1: User query received',
      done: true
    },
    {
      label: 'Step 2: NLP entity extraction',
      done: true
    },
    {
      label: 'Step 3: Cypher query generation',
      done: true
    },
    {
      label: 'Step 4: Neo4j graph search…',
      done: false
    },
    {
      label: 'Step 5: Llama 1B response…',
      done: false
    }
  ];

  return (
    <div
      style={{
        fontSize: '0.65rem',
        color: '#64748b',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.15rem',
        paddingLeft: '0.25rem'
      }}
    >
      {steps.map((s, i) => (
        <span
          key={i}
          style={{
            color: s.done
              ? '#818cf8'
              : '#475569'
          }}
        >
          {s.done ? '✓' : '◌'} {s.label}
        </span>
      ))}
    </div>
  );
}

/* ── Sub-component: Individual Chat Message ──────────────────────────── */
function ChatMessage({ msg }) {
  const [showCypher, setShowCypher] =
    useState(false);

  return (
    <div
      style={{
        alignSelf:
          msg.sender === 'user'
            ? 'flex-end'
            : 'flex-start',
        maxWidth: '90%'
      }}
    >
      {/* Bubble */}
      <div
        style={{
          padding: '0.75rem 1rem',

          borderRadius:
            msg.sender === 'user'
              ? '16px 16px 2px 16px'
              : '16px 16px 16px 2px',

          background:
            msg.sender === 'user'
              ? 'linear-gradient(135deg, #6366f1, #4f46e5)'
              : '#000000',

          border:
            msg.sender === 'user'
              ? 'none'
              : '1px solid #222222',

          color: '#ffffff',

          fontSize: '0.875rem',
          lineHeight: '1.55'
        }}
      >
        {msg.text}
      </div>

      {/* AI message metadata */}
      {msg.sender === 'ai' &&
        msg.entities &&
        msg.entities.length > 0 && (
          <div style={{ marginTop: '0.4rem' }}>
            {/* Entity Tags */}
            <div
              style={{
                fontSize: '0.65rem',
                color: '#818cf8',
                marginBottom: '0.25rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.2rem'
              }}
            >
              <Brain size={10} />
              Step 2 — Extracted entities:
            </div>

            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '0.25rem'
              }}
            >
              {msg.entities
                .slice(0, 8)
                .map((e, i) => (
                  <span
                    key={i}
                    style={{
                      fontSize: '0.65rem',
                      padding: '0.1rem 0.45rem',
                      borderRadius: '8px',
                      background:
                        'rgba(99,102,241,0.18)',
                      border:
                        '1px solid rgba(99,102,241,0.35)',
                      color: '#c7d2fe',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.15rem'
                    }}
                  >
                    <Tag size={8} />
                    {e}
                  </span>
                ))}
            </div>
          </div>
        )}

      {/* Matched Technologies (Step 4 output) */}
      {msg.sender === 'ai' &&
        msg.matched_techs?.length > 0 && (
          <div
            style={{
              marginTop: '0.3rem',
              fontSize: '0.65rem',
              color: '#67e8f9',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem',
              flexWrap: 'wrap'
            }}
          >
            <Network size={9} />

            <span
              style={{
                color: '#475569'
              }}
            >
              Step 4 graph matched:
            </span>

            {msg.matched_techs
              .slice(0, 4)
              .map((t, i) => (
                <span
                  key={i}
                  style={{
                    color: '#93c5fd'
                  }}
                >
                  {t}
                  {i <
                  msg.matched_techs.length - 1
                    ? ' →'
                    : ''}
                </span>
              ))}
          </div>
        )}

      {/* Cypher Queries Toggle (Step 3 transparency) */}
      {msg.sender === 'ai' &&
        msg.cypher_queries?.length > 0 && (
          <div
            style={{
              marginTop: '0.35rem'
            }}
          >
            <button
              onClick={() =>
                setShowCypher(v => !v)
              }
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                fontSize: '0.62rem',
                color: '#64748b',
                background: 'none',
                cursor: 'pointer',
                padding: 0
              }}
            >
              <Code2 size={9} />

              {showCypher
                ? 'Hide'
                : 'View'}{' '}
              Cypher queries (Step 3)

              {showCypher ? (
                <ChevronUp size={9} />
              ) : (
                <ChevronDown size={9} />
              )}
            </button>

            {showCypher && (
              <div
                style={{
                  marginTop: '0.3rem',
                  background: '#0d1117',
                  borderRadius: '8px',
                  padding: '0.5rem 0.65rem',
                  fontSize: '0.6rem',
                  color: '#7dd3fc',
                  fontFamily: 'monospace',
                  border:
                    '1px solid rgba(99,102,241,0.25)',
                  maxHeight: '120px',
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap'
                }}
              >
                {msg.cypher_queries[0]}
              </div>
            )}
          </div>
        )}

      {/* Course Cards (Step 5 output) */}
      {msg.courses?.length > 0 && (
        <div
          style={{
            marginTop: '0.6rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.45rem'
          }}
        >
          <span
            style={{
              fontSize: '0.7rem',
              color: '#818cf8',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem'
            }}
          >
            <BookOpen size={11} />
            Step 5 — Graph-matched courses:
          </span>

          {msg.courses
            .slice(0, 3)
            .map(c => (
              <div
                key={c.id}
                onClick={() =>
                  (window.location.href = `/course/${c.id}`)
                }
                style={{
                  background:
                    'rgba(15,23,42,0.75)',
                  padding: '0.55rem 0.7rem',
                  borderRadius: '10px',
                  border:
                    '1px solid rgba(255,255,255,0.09)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  cursor: 'pointer',
                  transition:
                    'border-color 0.15s'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor =
                    'rgba(99,102,241,0.45)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor =
                    'rgba(255,255,255,0.09)';
                }}
              >
                <img
                  src={
                    c.thumbnail ||
                    'https://images.unsplash.com/photo-1517694712202-14dd9538aa97'
                  }
                  alt=""
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '6px',
                    objectFit: 'cover',
                    flexShrink: 0
                  }}
                  onError={e => {
                    e.target.src =
                      'https://images.unsplash.com/photo-1517694712202-14dd9538aa97';
                  }}
                />

                <div
                  style={{
                    flex: 1,
                    minWidth: 0
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      color: 'white',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {c.title}
                  </div>

                  <div
                    style={{
                      fontSize: '0.68rem',
                      color: '#94a3b8'
                    }}
                  >
                    ★ {c.rating} · {c.department} ·{' '}
                    {c.difficulty} · ${c.price}
                  </div>

                  {c.recommendation_reason && (
                    <div
                      style={{
                        fontSize: '0.62rem',
                        color: '#818cf8',
                        marginTop: '0.1rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      <Sparkles
                        size={8}
                        style={{
                          marginRight: '0.2rem',
                          verticalAlign: 'middle'
                        }}
                      />
                      {c.recommendation_reason}
                    </div>
                  )}
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}