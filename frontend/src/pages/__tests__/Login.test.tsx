import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Login } from '../Login'

// Mock the auth store
vi.mock('../../store/authStore', () => ({
  useAuthStore: vi.fn((selector) =>
    selector({
      setAuth: vi.fn(),
    })
  ),
}))

// Mock the auth API
vi.mock('../../api/auth', () => ({
  authAPI: {
    login: vi.fn(),
  },
}))

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Login', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders email and password fields and submit button', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('••••••••')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument()
  })

  it('shows error on wrong credentials', async () => {
    const { authAPI } = await import('../../api/auth')
    vi.mocked(authAPI.login).mockRejectedValueOnce({
      response: { data: { detail: 'Invalid email or password' } },
    })

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const emailInput = screen.getByPlaceholderText('you@example.com') as HTMLInputElement
    const passwordInput = screen.getByPlaceholderText('••••••••') as HTMLInputElement
    const submitButton = screen.getByRole('button', { name: /Login/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'wrong' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password')).toBeInTheDocument()
    })
  })

  it('redirects to / on successful login', async () => {
    const { authAPI } = await import('../../api/auth')
    vi.mocked(authAPI.login).mockResolvedValueOnce({
      user: { id: '1', email: 'test@example.com', name: 'Test User', created_at: '2024-03-15T10:00:00Z' },
      access_token: 'token123',
      refresh_token: 'refresh123',
    })

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const emailInput = screen.getByPlaceholderText('you@example.com') as HTMLInputElement
    const passwordInput = screen.getByPlaceholderText('••••••••') as HTMLInputElement
    const submitButton = screen.getByRole('button', { name: /Login/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('disables button during loading', async () => {
    const { authAPI } = await import('../../api/auth')
    vi.mocked(authAPI.login).mockImplementationOnce(
      () =>
        new Promise(() => {
          // Intentionally not resolving to keep loading state
        })
    )

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const emailInput = screen.getByPlaceholderText('you@example.com') as HTMLInputElement
    const passwordInput = screen.getByPlaceholderText('••••••••') as HTMLInputElement
    const submitButton = screen.getByRole('button', { name: /Login/i }) as HTMLButtonElement

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    expect(submitButton).toBeDisabled()
    expect(screen.getByText('Logging in...')).toBeInTheDocument()
  })

  it('shows API error detail message', async () => {
    const { authAPI } = await import('../../api/auth')
    vi.mocked(authAPI.login).mockRejectedValueOnce({
      response: { data: { detail: 'Account locked' } },
    })

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const emailInput = screen.getByPlaceholderText('you@example.com') as HTMLInputElement
    const passwordInput = screen.getByPlaceholderText('••••••••') as HTMLInputElement
    const submitButton = screen.getByRole('button', { name: /Login/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Account locked')).toBeInTheDocument()
    })
  })
})
