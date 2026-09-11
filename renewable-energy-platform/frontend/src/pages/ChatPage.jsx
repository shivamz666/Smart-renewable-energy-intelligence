import React, { useContext, useState, useRef, useEffect } from 'react'
import { MessageSquare, Send, Cpu, AlertTriangle } from 'lucide-react'
import { AppContext } from '../App'
import { sendChatMessage } from '../api'

const SUGGESTED = [
  'Which assets are underperforming?',
  'Why is WT-07 underperforming?',
  'Which assets have the highest maintenance risk?',
  'What is the expected generation for the next 6 hours?',
  'Is renewable generation expected to exceed demand?',
  'What should the operator consider doing?',
  'Give me the current park health summary.',
  'What is the current weather and solar irradiance?',
]

export default function ChatPage() {
  const { state } = useContext(AppContext)
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hello! I'm the IBM Granite AI assistant for your Smart Renewable Energy Intelligence Platform.\n\nI can help you understand complex renewable energy data, identify risks, and support your decision-making.\n\n**Important:** I provide decision support only. All data in this system is DEMO / SIMULATED.\n\nWhat would you like to know?",
      source: 'IBM Granite AI (Mock Mode)',
      time: new Date().toLocaleTimeString(),
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return

    const userMsg = { role: 'user', text: text.trim(), time: new Date().toLocaleTimeString() }
    setMessages(m => [...m, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await sendChatMessage(text.trim())
      const d = res.data
      setMessages(m => [...m, {
        role: 'assistant',
        text: d.response,
        source: d.source,
        model: d.model,
        confidence: d.confidence,
        note: d.note,
        time: new Date().toLocaleTimeString(),
      }])
    } catch (e) {
      setMessages(m => [...m, {
        role: 'assistant',
        text: '❌ Unable to connect to the AI backend. Please ensure the Python server is running.',
        source: 'Error',
        time: new Date().toLocaleTimeString(),
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)', gap: 0 }}>
      {/* Header */}
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: '12px 12px 0 0', padding: '14px 20px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
      }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ background: 'linear-gradient(135deg,#f472b6,#a855f7)', borderRadius: 8, padding: 6 }}>
              <Cpu size={16} color="#fff" />
            </div>
            IBM Granite AI Assistant
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 2 }}>
            Powered by IBM Granite — Natural language decision support • DATA: DEMO / SIMULATED
          </div>
        </div>
        <div style={{
          fontSize: 11, background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)',
          color: '#a5b4fc', borderRadius: 6, padding: '4px 10px'
        }}>
          🛡 Decision Support Only
        </div>
      </div>

      {/* Message area */}
      <div style={{
        flex: 1, overflowY: 'auto',
        background: 'var(--bg)', border: '1px solid var(--border)',
        borderTop: 'none', borderBottom: 'none',
        padding: '20px'
      }}>
        <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
          {messages.map((msg, i) => (
            <Message key={i} msg={msg} />
          ))}
          {loading && <ThinkingBubble />}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Suggestions */}
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderTop: 'none', padding: '10px 20px', overflowX: 'auto'
      }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'nowrap' }}>
          {SUGGESTED.map((s, i) => (
            <button key={i} onClick={() => sendMessage(s)} disabled={loading} style={{
              background: 'var(--surface2)', border: '1px solid var(--border)',
              color: 'var(--muted)', borderRadius: 16, padding: '5px 12px',
              fontSize: 11, whiteSpace: 'nowrap', flexShrink: 0,
              transition: 'all 0.15s'
            }}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: '0 0 12px 12px', borderTop: 'none', padding: '14px 20px',
        display: 'flex', gap: 12
      }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage(input)}
          placeholder="Ask about your renewable energy park..."
          disabled={loading}
          style={{
            flex: 1, background: 'var(--surface2)', border: '1px solid var(--border)',
            borderRadius: 8, padding: '10px 14px', color: 'var(--text)',
            fontSize: 13, resize: 'none'
          }}
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
          style={{
            background: loading || !input.trim() ? 'var(--surface2)' : 'var(--accent)',
            border: 'none', borderRadius: 8, padding: '10px 16px',
            color: loading || !input.trim() ? 'var(--muted)' : '#fff',
            display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600, fontSize: 13,
            transition: 'all 0.2s'
          }}
        >
          {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : <Send size={16} />}
          Send
        </button>
      </div>
    </div>
  )
}

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
      <div style={{
        maxWidth: '80%',
        background: isUser ? 'rgba(56,189,248,0.12)' : 'var(--surface)',
        border: `1px solid ${isUser ? 'rgba(56,189,248,0.3)' : 'var(--border)'}`,
        borderRadius: isUser ? '16px 16px 4px 16px' : '4px 16px 16px 16px',
        padding: '12px 16px',
      }}>
        {!isUser && (
          <div style={{ fontSize: 10, color: '#f472b6', fontWeight: 600, marginBottom: 6, display: 'flex', gap: 8 }}>
            <span>🤖 IBM Granite AI</span>
            {msg.source && <span style={{ color: 'var(--muted)' }}>• {msg.source}</span>}
          </div>
        )}
        <div style={{
          fontSize: 13, lineHeight: 1.7, color: 'var(--text)',
          whiteSpace: 'pre-wrap', wordBreak: 'break-word'
        }}>
          {formatMarkdown(msg.text)}
        </div>
        <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 6, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <span>{msg.time}</span>
          {msg.note && <span style={{ color: '#f59e0b' }}>⚠️ {msg.note}</span>}
          {msg.confidence && <span>Confidence: {(msg.confidence * 100).toFixed(0)}%</span>}
        </div>
      </div>
    </div>
  )
}

function ThinkingBubble() {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: '4px 16px 16px 16px', padding: '12px 20px',
        display: 'flex', alignItems: 'center', gap: 8
      }}>
        <div style={{ display: 'flex', gap: 4 }}>
          {[0, 1, 2].map(i => (
            <div key={i} style={{
              width: 8, height: 8, borderRadius: '50%', background: '#f472b6',
              animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite`
            }} />
          ))}
        </div>
        <span style={{ fontSize: 12, color: 'var(--muted)' }}>IBM Granite is analyzing...</span>
      </div>
    </div>
  )
}

// Simple markdown-like formatter
function formatMarkdown(text) {
  if (!text) return null
  const lines = text.split('\n')
  return lines.map((line, i) => {
    if (line.startsWith('**') && line.endsWith('**')) {
      return <strong key={i} style={{ color: 'var(--accent)', display: 'block' }}>{line.slice(2, -2)}<br /></strong>
    }
    if (line.startsWith('• ') || line.startsWith('- ')) {
      return <div key={i} style={{ paddingLeft: 16, marginBottom: 2 }}>• {line.slice(2)}</div>
    }
    return <span key={i}>{line}{i < lines.length - 1 ? '\n' : ''}</span>
  })
}
