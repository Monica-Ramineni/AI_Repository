// Test comment
'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Settings, Bot, User, Key, MessageSquare, Upload, FileText, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { getApiUrl } from '@/lib/config'

// Function to strip markdown and LaTeX notation
function stripMarkdownAndLatex(text: string): string {
  return text
    // Remove LaTeX block and inline math
    .replace(/\\\[|\\\]/g, '') // Remove \[ and \]
    .replace(/\\\(|\\\)/g, '') // Remove \( and \)
    .replace(/\\begin\{[^}]*\}[\s\S]*?\\end\{[^}]*\}/g, '')
    .replace(/\$\$[\s\S]*?\$\$/g, '')
    .replace(/\$([^$]+)\$/g, '$1')
    // Remove markdown code blocks and inline code
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`([^`]+)`/g, '$1')
    // Remove markdown headers, bold, italic, links, lists
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/^[\s]*[-*+]\s+/gm, '')
    .replace(/^[\s]*\d+\.\s+/gm, '')
    // Remove LaTeX commands and curly braces
    .replace(/\\[a-zA-Z]+(\{[^}]*\})?/g, '')
    .replace(/[{}]/g, '')
    // Remove unnecessary equal signs surrounded by spaces
    .replace(/\s=\s/g, ' ')
    // Remove any leftover backslashes
    .replace(/\\/g, '')
    // Clean up extra whitespace
    .replace(/\n\s*\n/g, '\n\n')
    .replace(/[ ]{2,}/g, ' ')
    .trim();
}

interface Message {
  id: string
  content: string
  role: 'user' | 'ai'
  timestamp: Date
}

interface ChatSettings {
  apiKey: string
  developerMessage: string
  model: string
  useRag: boolean
  sessionId: string
}

interface DocumentInfo {
  session_id: string
  total_chunks: number
  documents: { filename: string; filetype: string; chunks_count: number }[]
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [documentInfo, setDocumentInfo] = useState<DocumentInfo | null>(null)
  const [settings, setSettings] = useState<ChatSettings>({
    apiKey: '',
    developerMessage: 'You are a helpful AI assistant. When using RAG mode, use the provided document information when relevant.',
    model: 'gpt-4.1-mini',
    useRag: false,
    sessionId: ''
  })
  const [summary, setSummary] = useState<string | null>(null)
  const [summarizing, setSummarizing] = useState<string | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (!settings.sessionId) {
      setSettings(prev => ({ ...prev, sessionId: crypto.randomUUID() }))
    }
  }, [settings.sessionId])

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    const lower = file.name.toLowerCase()
    if (!lower.endsWith('.pdf') && !lower.endsWith('.docx') && !lower.endsWith('.txt')) {
      alert('Please upload a PDF, DOCX, or TXT file')
      return
    }
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('session_id', settings.sessionId)
    try {
      const response = await fetch('/api/upload-document', {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) throw new Error('Upload failed')
      await fetchDocumentInfo()
      setSettings(prev => ({ ...prev, useRag: true }))
      alert(file.name + ' uploaded and indexed!')
    } catch (error) {
      alert('Failed to upload document.')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const fetchDocumentInfo = async () => {
    try {
      const response = await fetch(`/api/documents/${settings.sessionId}`)
      if (response.ok) {
        const info = await response.json()
        setDocumentInfo(info)
      }
    } catch {}
  }

  const clearDocuments = async () => {
    try {
      const response = await fetch(`/api/documents/${settings.sessionId}`, { method: 'DELETE' })
      if (response.ok) {
        setDocumentInfo(null)
        setSettings(prev => ({ ...prev, useRag: false }))
        alert('Documents cleared!')
      }
    } catch {
      alert('Failed to clear documents.')
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !settings.apiKey.trim()) return
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          developer_message: settings.developerMessage,
          user_message: inputMessage,
          model: settings.model,
          api_key: settings.apiKey,
          session_id: settings.sessionId,
          use_rag: settings.useRag
        }),
      })
      if (!response.body) throw new Error('No response body')
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '',
        role: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        accumulatedContent += chunk
        setMessages(prev =>
          prev.map(msg =>
            msg.id === aiMessage.id
              ? { ...msg, content: stripMarkdownAndLatex(accumulatedContent) }
              : msg
          )
        )
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: 'Sorry, there was an error processing your request.',
        role: 'ai',
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  const handleSummarize = async (doc: { filename: string; filetype: string }) => {
    setSummarizing(doc.filename)
    try {
      const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: settings.sessionId,
          filename: doc.filename,
          filetype: doc.filetype,
        }),
      })
      if (!response.ok) throw new Error('Failed to summarize document')
      const data = await response.json()
      setSummary(data.summary)
    } catch (e) {
      alert('Failed to summarize document.')
    } finally {
      setSummarizing(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-50 to-dark-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="text-center mb-8">
          <h1 className="title-calligrapher">AI Chat Interface with RAG</h1>
          <p className="subtitle">Upload PDFs and chat with them using AIMakerSpace</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-dark-900 flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Settings
                </h2>
                <button onClick={() => setShowSettings(!showSettings)} className="text-dark-500 hover:text-dark-700">
                  <Settings className="w-5 h-5" />
                </button>
              </div>
              {showSettings && (
                <div className="space-y-4 animate-fade-in">
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">OpenAI API Key</label>
                    <input type="password" value={settings.apiKey} onChange={(e) => setSettings(prev => ({ ...prev, apiKey: e.target.value }))} placeholder="sk-..." className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">System Message</label>
                    <textarea value={settings.developerMessage} onChange={(e) => setSettings(prev => ({ ...prev, developerMessage: e.target.value }))} placeholder="You are a helpful AI assistant..." className="input-field" rows={3} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">Model</label>
                    <select value={settings.model} onChange={(e) => setSettings(prev => ({ ...prev, model: e.target.value }))} className="input-field">
                      <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
                      <option value="gpt-4o">GPT-4o</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    </select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="useRag" checked={settings.useRag} onChange={(e) => setSettings(prev => ({ ...prev, useRag: e.target.checked }))} className="rounded border-dark-300 text-primary-600 focus:ring-primary-500" />
                    <label htmlFor="useRag" className="text-sm font-medium text-dark-700">Use RAG (Document Chat)</label>
                  </div>
                  {settings.useRag && (
                    <div className="p-3 bg-primary-50 rounded-lg">
                      <p className="text-sm text-primary-700">RAG mode enabled. Upload a PDF to chat with it!</p>
                    </div>
                  )}
                </div>
              )}
              <div className="mt-6 border-t pt-6">
                <h3 className="text-lg font-semibold text-dark-900 mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Document Upload
                </h3>
                <div className="space-y-4">
                  <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt" onChange={handleFileUpload} className="hidden" />
                  <button onClick={() => fileInputRef.current?.click()} disabled={uploading} className="w-full btn-primary flex items-center justify-center gap-2">
                    <Upload className="w-4 h-4" />
                    {uploading ? 'Uploading...' : 'Upload File'}
                  </button>
                  <p className="text-xs text-dark-500 mt-1">Supported file types: PDF, DOCX, TXT</p>
                  {documentInfo && documentInfo.documents && documentInfo.documents.length > 0 && (
                    <div className="p-3 bg-green-50 rounded-lg">
                      <p className="text-sm text-green-700 font-semibold mb-2">Uploaded Documents:</p>
                      <ul className="space-y-2">
                        {documentInfo.documents.map((doc, idx) => (
                          <li key={doc.filename + idx} className="flex items-center justify-between bg-green-100 rounded px-2 py-1">
                            <span className="font-mono text-xs">{doc.filename}</span>
                            <span className="text-xs ml-2">[{doc.filetype.toUpperCase()}] | {doc.chunks_count} chunks</span>
                            <button className="ml-2 btn-secondary btn-xs" onClick={() => handleSummarize(doc)} disabled={summarizing === doc.filename}>
                              {summarizing === doc.filename ? 'Summarizing...' : 'Summarize'}
                            </button>
                          </li>
                        ))}
                      </ul>
                      <button onClick={clearDocuments} className="mt-2 text-xs text-red-600 hover:text-red-800 flex items-center gap-1">
                        <Trash2 className="w-3 h-3" />
                        Clear documents
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          <div className="lg:col-span-3">
            <div className="card h-[600px] flex flex-col">
              <div className="flex items-center justify-between p-4 border-b border-dark-200">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-primary-600" />
                  <h2 className="text-lg font-semibold text-dark-900">Chat</h2>
                  {settings.useRag && documentInfo && (
                    <span className="px-2 py-1 text-xs bg-primary-100 text-primary-700 rounded-full">RAG Active</span>
                  )}
                </div>
                <button onClick={clearChat} className="text-dark-500 hover:text-dark-700 text-sm">Clear Chat</button>
              </div>
              <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-dark-500 py-8">
                    <Bot className="w-12 h-12 mx-auto mb-4 text-dark-300" />
                    <p>Start a conversation or upload a PDF to chat with it!</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div key={message.id} className={cn("flex gap-3", message.role === 'user' ? 'justify-end' : 'justify-start')}>
                      {message.role === 'ai' && (
                        <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                          <Bot className="w-4 h-4 text-primary-600" />
                        </div>
                      )}
                      <div className={cn("max-w-[80%] rounded-lg px-4 py-2", message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-dark-100 text-dark-900')}>
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">{message.timestamp.toLocaleTimeString()}</p>
                      </div>
                      {message.role === 'user' && (
                        <div className="w-8 h-8 rounded-full bg-dark-200 flex items-center justify-center">
                          <User className="w-4 h-4 text-dark-600" />
                        </div>
                      )}
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>
              <div className="p-4 border-t border-dark-200">
                <div className="flex gap-2">
                  <textarea value={inputMessage} onChange={(e) => setInputMessage(e.target.value)} onKeyPress={handleKeyPress} placeholder="Type your message..." className="flex-1 input-field resize-none" rows={1} disabled={isLoading} />
                  <button onClick={handleSendMessage} disabled={isLoading || !inputMessage.trim() || !settings.apiKey.trim()} className="btn-primary px-4 py-2">
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        {summary && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-lg w-full">
              <h2 className="text-lg font-bold mb-2">Document Summary</h2>
              <pre className="whitespace-pre-wrap text-sm mb-4 max-h-96 overflow-y-auto">{summary}</pre>
              <button className="btn-primary" onClick={() => setSummary(null)}>Close</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 