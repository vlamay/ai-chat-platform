import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageBubble } from '../MessageBubble'
import type { Message } from '../../types'

describe('MessageBubble', () => {
  it('renders user message as plain text', () => {
    const message: Message = {
      id: '1',
      chat_id: 'chat-1',
      role: 'user',
      content: 'Hello World',
      created_at: '2024-03-15T10:00:00Z',
    }

    render(<MessageBubble message={message} />)

    expect(screen.getByText('Hello World')).toBeInTheDocument()
    expect(screen.getByText('Hello World')).toHaveClass('whitespace-pre-wrap')
  })

  it('renders assistant message with markdown', () => {
    const message: Message = {
      id: '2',
      chat_id: 'chat-1',
      role: 'assistant',
      content: '**Bold text** and `code`',
      created_at: '2024-03-15T10:00:00Z',
    }

    render(<MessageBubble message={message} />)

    const container = screen.getByText(/Bold text/).parentElement
    expect(container).toHaveClass('prose')
  })

  it('shows correct timestamp format', () => {
    const message: Message = {
      id: '3',
      chat_id: 'chat-1',
      role: 'user',
      content: 'Test message',
      created_at: '2024-03-15T14:30:00Z',
    }

    render(<MessageBubble message={message} />)

    // Check that time is displayed (format depends on locale)
    const timeElements = screen.getAllByText(/\d{1,2}:\d{2}/)
    expect(timeElements.length).toBeGreaterThan(0)
  })

  it('does not render markdown in user messages', () => {
    const message: Message = {
      id: '4',
      chat_id: 'chat-1',
      role: 'user',
      content: '**This should not be bold**',
      created_at: '2024-03-15T10:00:00Z',
    }

    render(<MessageBubble message={message} />)

    // User messages should render as plain text
    expect(screen.getByText('**This should not be bold**')).toBeInTheDocument()
  })
})
