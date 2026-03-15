import { http, HttpResponse } from 'msw'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/api/v1/auth/register`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string }

    // Mock duplicate email check
    if (body.email === 'existing@example.com') {
      return HttpResponse.json(
        { detail: 'Email already registered' },
        { status: 400 }
      )
    }

    return HttpResponse.json(
      {
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        token_type: 'bearer',
        user: { id: '1', email: body.email, name: 'Test User' },
      },
      { status: 201 }
    )
  }),

  http.post(`${API_BASE}/api/v1/auth/login`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string }

    // Mock failed login
    if (body.password !== 'password123') {
      return HttpResponse.json(
        { detail: 'Invalid email or password' },
        { status: 401 }
      )
    }

    return HttpResponse.json({
      access_token: 'mock_access_token',
      refresh_token: 'mock_refresh_token',
      token_type: 'bearer',
      user: { id: '1', email: body.email, name: 'Test User' },
    })
  }),

  http.post(`${API_BASE}/api/v1/auth/refresh`, () => {
    return HttpResponse.json({
      access_token: 'new_mock_access_token',
      refresh_token: 'new_mock_refresh_token',
      token_type: 'bearer',
      user: { id: '1', email: 'test@example.com', name: 'Test User' },
    })
  }),

  // Chats endpoints
  http.post(`${API_BASE}/api/v1/chats`, () => {
    return HttpResponse.json(
      {
        id: 'chat-1',
        title: 'New Chat',
        model: 'claude-3-sonnet-20240229',
        user_id: '1',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      { status: 201 }
    )
  }),

  http.get(`${API_BASE}/api/v1/chats`, () => {
    return HttpResponse.json([
      {
        id: 'chat-1',
        title: 'Test Chat',
        model: 'claude-3-sonnet-20240229',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 5,
      },
    ])
  }),

  // Messages endpoints
  http.get(`${API_BASE}/api/v1/messages/:chat_id`, () => {
    return HttpResponse.json([
      {
        id: 'msg-1',
        chat_id: 'chat-1',
        role: 'user',
        content: 'Hello',
        created_at: new Date().toISOString(),
      },
      {
        id: 'msg-2',
        chat_id: 'chat-1',
        role: 'assistant',
        content: 'Hi there!',
        created_at: new Date().toISOString(),
      },
    ])
  }),

  http.post(`${API_BASE}/api/v1/messages/:chat_id/stream`, () => {
    return HttpResponse.json({ status: 'ok' })
  }),
]
