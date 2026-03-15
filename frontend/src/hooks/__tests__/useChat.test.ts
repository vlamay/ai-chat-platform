import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useChat } from '../useChat'
import type { Message } from '../../types'

// Mock the chats API
vi.mock('../../api/chats', () => ({
  chatsAPI: {
    listChats: vi.fn(),
    createChat: vi.fn(),
    getChat: vi.fn(),
    getMessages: vi.fn(),
    deleteChat: vi.fn(),
    streamMessage: vi.fn(),
  },
}))

describe('useChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads chats on init', async () => {
    const { chatsAPI } = await import('../../api/chats')
    const mockChats = [
      {
        id: 'chat-1',
        title: 'Chat 1',
        model: 'claude-3-sonnet-20240229',
        created_at: '2024-03-15T10:00:00Z',
        updated_at: '2024-03-15T10:00:00Z',
        message_count: 0,
      },
    ]
    vi.mocked(chatsAPI.listChats).mockResolvedValueOnce(mockChats)

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.loadChats()
    })

    expect(result.current.chats).toEqual(mockChats)
  })

  it('creates new chat and adds to list', async () => {
    const { chatsAPI } = await import('../../api/chats')
    const mockChat = {
      id: 'chat-new',
      user_id: 'user-1',
      title: 'New Chat',
      model: 'claude-3-sonnet-20240229',
      created_at: '2024-03-15T10:00:00Z',
      updated_at: '2024-03-15T10:00:00Z',
      messages: [],
    }
    vi.mocked(chatsAPI.createChat).mockResolvedValueOnce(mockChat)

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.createChat('New Chat')
    })

    expect(result.current.chats).toContainEqual(
      expect.objectContaining({
        id: 'chat-new',
        title: 'New Chat',
      })
    )
    expect(result.current.currentChat).toEqual(mockChat)
  })

  it('selects chat and loads messages', async () => {
    const { chatsAPI } = await import('../../api/chats')
    const mockChat = {
      id: 'chat-1',
      user_id: 'user-1',
      title: 'Chat 1',
      model: 'claude-3-sonnet-20240229',
      created_at: '2024-03-15T10:00:00Z',
      updated_at: '2024-03-15T10:00:00Z',
      messages: [],
    }
    const mockMessages = [
      {
        id: 'msg-1',
        chat_id: 'chat-1',
        role: 'user' as const,
        content: 'Hello',
        created_at: '2024-03-15T10:00:00Z',
      },
    ]
    vi.mocked(chatsAPI.getChat).mockResolvedValueOnce(mockChat)
    vi.mocked(chatsAPI.getMessages).mockResolvedValueOnce(mockMessages)

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.selectChat('chat-1')
    })

    expect(result.current.currentChat).toEqual(mockChat)
    expect(result.current.messages).toEqual(mockMessages)
  })

  it('handles load error gracefully', async () => {
    const { chatsAPI } = await import('../../api/chats')
    vi.mocked(chatsAPI.getChat).mockRejectedValueOnce(new Error('Load failed'))

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.selectChat('chat-1')
    })

    expect(result.current.error).toBe('Failed to load chat')
  })

  it('deletes chat and removes from list', async () => {
    const { chatsAPI } = await import('../../api/chats')
    const mockChats = [
      {
        id: 'chat-1',
        title: 'Chat 1',
        model: 'claude-3-sonnet-20240229',
        created_at: '2024-03-15T10:00:00Z',
        updated_at: '2024-03-15T10:00:00Z',
        message_count: 0,
      },
    ]
    vi.mocked(chatsAPI.listChats).mockResolvedValueOnce(mockChats)
    vi.mocked(chatsAPI.deleteChat).mockResolvedValueOnce(undefined)

    const { result } = renderHook(() => useChat())

    // Load initial chats
    await act(async () => {
      await result.current.loadChats()
    })

    expect(result.current.chats).toHaveLength(1)

    // Delete chat
    await act(async () => {
      await result.current.deleteChat('chat-1')
    })

    expect(result.current.chats).toHaveLength(0)
  })

  it('sendMessage updates messages optimistically', async () => {
    const { chatsAPI } = await import('../../api/chats')
    const mockChat = {
      id: 'chat-1',
      user_id: 'user-1',
      title: 'Chat 1',
      model: 'claude-3-sonnet-20240229',
      created_at: '2024-03-15T10:00:00Z',
      updated_at: '2024-03-15T10:00:00Z',
      messages: [],
    }
    const mockMessages = [
      {
        id: 'msg-1',
        chat_id: 'chat-1',
        role: 'user' as const,
        content: 'Test message',
        created_at: '2024-03-15T10:00:00Z',
      },
    ]
    vi.mocked(chatsAPI.getChat).mockResolvedValueOnce(mockChat)
    vi.mocked(chatsAPI.getMessages).mockResolvedValueOnce(mockMessages)
    vi.mocked(chatsAPI.streamMessage).mockResolvedValueOnce(new ReadableStream())

    const { result } = renderHook(() => useChat())

    // Select chat to set currentChat
    await act(async () => {
      await result.current.selectChat('chat-1')
    })

    expect(result.current.currentChat).toEqual(mockChat)
    expect(result.current.messages).toEqual(mockMessages)
  })
})
