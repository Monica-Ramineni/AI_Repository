// Test comment
'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Settings, Bot, User, Key, MessageSquare } from 'lucide-react'
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
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [settings, setSettings] = useState<ChatSettings>({
    apiKey: '',
    developerMessage: 'You are a helpful AI assistant.',
    model: 'gpt-4.1-mini'
  })
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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
      const response = await fetch('https://the-ai-engineer-challenge-xi-ten.vercel.app/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          developer_message: settings.developerMessage,
          user_message: inputMessage,
          model: settings.model,
          api_key: settings.apiKey
        }),
      })

      if (!response.body) throw new Error('No response body')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''

      // Add an empty AI message first
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

        // Remove markdown/LaTeX as it streams in
        setMessages(prev =>
          prev.map(msg =>
            msg.id === aiMessage.id
              ? { ...msg, content: stripMarkdownAndLatex(accumulatedContent) }
              : msg
          )
        )
      }
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: 'Sorry, there was an error processing your request. Please check your API key and try again.',
        role: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-50 to-dark-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="title-calligrapher">AI Chat Interface</h1>
          <p className="subtitle">Experience real-time conversations with AI</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Settings Panel */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-dark-900 flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Settings
                </h2>
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="text-dark-500 hover:text-dark-700"
                >
                  <Settings className="w-5 h-5" />
                </button>
              </div>

              {showSettings && (
                <div className="space-y-4 animate-fade-in">
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      OpenAI API Key
                    </label>
                    <input
                      type="password"
                      value={settings.apiKey}
                      onChange={(e) => setSettings(prev => ({ ...prev, apiKey: e.target.value }))}
                      placeholder="sk-..."
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Developer Message
                    </label>
                    <textarea
                      value={settings.developerMessage}
                      onChange={(e) => setSettings(prev => ({ ...prev, developerMessage: e.target.value }))}
                      placeholder="System instructions for the AI..."
                      rows={3}
                      className="input-field resize-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Model
                    </label>
                    <select
                      value={settings.model}
                      onChange={(e) => setSettings(prev => ({ ...prev, model: e.target.value }))}
                      className="input-field"
                    >
                      <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
                      <option value="gpt-4">GPT-4</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    </select>
                  </div>

                  <button
                    onClick={clearChat}
                    className="btn-secondary w-full"
                  >
                    Clear Chat
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <div className="card h-[600px] flex flex-col">
              {/* Messages */}
              <div 
                ref={chatContainerRef}
                className="flex-1 overflow-y-auto p-4 space-y-4"
              >
                {messages.length === 0 ? (
                  <div className="text-center text-dark-500 mt-20">
                    <MessageSquare className="w-16 h-16 mx-auto mb-4 text-dark-300" />
                    <p className="text-lg">Start a conversation with AI</p>
                    <p className="text-sm">Enter your message below to begin</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        'chat-message flex items-start gap-3',
                        message.role === 'user' ? 'user-message' : 'ai-message'
                      )}
                    >
                      <div className="flex-shrink-0">
                        {message.role === 'user' ? (
                          <User className="w-6 h-6 text-white" />
                        ) : (
                          <Bot className="w-6 h-6 text-primary-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="whitespace-pre-wrap">
                          {message.role === 'ai' ? stripMarkdownAndLatex(message.content) : message.content}
                        </p>
                        <p className="text-xs opacity-70 mt-2">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}

                {isLoading && (
                  <div className="chat-message ai-message flex items-start gap-3">
                    <Bot className="w-6 h-6 text-primary-600 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="typing-indicator">
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t border-dark-200 p-4">
                <div className="flex gap-3">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    rows={1}
                    className="input-field resize-none flex-1"
                    disabled={isLoading || !settings.apiKey.trim()}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={isLoading || !inputMessage.trim() || !settings.apiKey.trim()}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
                {!settings.apiKey.trim() && (
                  <p className="text-sm text-red-600 mt-2">
                    Please enter your OpenAI API key in settings
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 