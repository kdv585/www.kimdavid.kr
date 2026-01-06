import { useState, useRef, useEffect } from 'react'
import { ragApi } from '../services/api'
import './RAGChat.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{
    content: string
    metadata: Record<string, any>
  }>
  timestamp: Date
}

function RAGChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await ragApi.query(input.trim())

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : '질의 처리 중 오류가 발생했습니다.')
      const errorMessage: Message = {
        role: 'assistant',
        content: '죄송합니다. 질의 처리 중 오류가 발생했습니다.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="rag-chat">
      <div className="rag-chat-header">
        <h3>🤖 LangChain RAG 챗봇</h3>
        <p>문서 기반 질의응답 시스템에 질문해보세요</p>
      </div>

      <div className="rag-chat-messages">
        {messages.length === 0 && (
          <div className="rag-chat-empty">
            <p>안녕하세요! LangChain RAG 시스템입니다.</p>
            <p>문서에 대한 질문을 입력해주세요.</p>
            <div className="rag-chat-examples">
              <p>예시 질문:</p>
              <ul>
                <li>LangChain이 무엇인가요?</li>
                <li>RAG는 어떻게 작동하나요?</li>
                <li>pgvector는 어떤 용도로 사용되나요?</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`rag-message rag-message-${message.role}`}
          >
            <div className="rag-message-content">
              <div className="rag-message-role">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="rag-message-text">
                {message.content}
              </div>
            </div>

            {message.sources && message.sources.length > 0 && (
              <div className="rag-message-sources">
                <p className="rag-sources-title">📚 참고 문서:</p>
                {message.sources.map((source, idx) => (
                  <div key={idx} className="rag-source-item">
                    <p className="rag-source-content">
                      {source.content}
                    </p>
                    {source.metadata && Object.keys(source.metadata).length > 0 && (
                      <div className="rag-source-metadata">
                        {Object.entries(source.metadata).map(([key, value]) => (
                          <span key={key} className="rag-source-tag">
                            {key}: {String(value)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            <div className="rag-message-time">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="rag-message rag-message-assistant">
            <div className="rag-message-content">
              <div className="rag-message-role">🤖</div>
              <div className="rag-message-text">
                <div className="rag-loading">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                답변을 생성하고 있습니다...
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="rag-error">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="rag-chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="질문을 입력하세요..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          {isLoading ? '전송 중...' : '전송'}
        </button>
      </form>
    </div>
  )
}

export default RAGChat
