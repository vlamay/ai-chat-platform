import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can register with valid credentials', async ({ page }) => {
    await page.goto('/register')

    // Check that register page is displayed
    await expect(page.getByText('Create your account')).toBeVisible()

    // Fill in registration form
    await page.fill('input[type="email"]', `user-${Date.now()}@example.com`)
    await page.fill('input[placeholder="Your name"]', 'Test User')
    await page.fill('input[type="password"]:first-of-type', 'password123')
    await page.fill('input[type="password"]:last-of-type', 'password123')

    // Submit form
    await page.click('button:has-text("Sign up")')

    // Should redirect to chat page
    await expect(page).toHaveURL('/')
    await expect(page.getByText('New Chat')).toBeVisible()
  })

  test('user sees error on duplicate email', async ({ page }) => {
    const email = `duplicate-${Date.now()}@example.com`

    // Register first user
    await page.goto('/register')
    await page.fill('input[type="email"]', email)
    await page.fill('input[placeholder="Your name"]', 'First User')
    await page.fill('input[type="password"]:first-of-type', 'password123')
    await page.fill('input[type="password"]:last-of-type', 'password123')
    await page.click('button:has-text("Sign up")')

    // Wait for redirect
    await expect(page).toHaveURL('/')

    // Logout (navigate to register)
    await page.goto('/register')

    // Try to register with same email
    await page.fill('input[type="email"]', email)
    await page.fill('input[placeholder="Your name"]', 'Second User')
    await page.fill('input[type="password"]:first-of-type', 'password123')
    await page.fill('input[type="password"]:last-of-type', 'password123')
    await page.click('button:has-text("Sign up")')

    // Should see error message
    await expect(page.getByText(/already registered|already exists/i)).toBeVisible()
  })

  test('user can login after registration', async ({ page }) => {
    const email = `logintest-${Date.now()}@example.com`
    const password = 'password123'

    // Register
    await page.goto('/register')
    await page.fill('input[type="email"]', email)
    await page.fill('input[placeholder="Your name"]', 'Login Test User')
    await page.fill('input[type="password"]:first-of-type', password)
    await page.fill('input[type="password"]:last-of-type', password)
    await page.click('button:has-text("Sign up")')

    // Should be on chat page
    await expect(page).toHaveURL('/')

    // Logout by clearing localStorage and going to login
    await page.evaluate(() => localStorage.clear())
    await page.goto('/login')

    // Login with same credentials
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button:has-text("Login")')

    // Should redirect to chat page
    await expect(page).toHaveURL('/')
    await expect(page.getByText('New Chat')).toBeVisible()
  })

  test('user is redirected to login when accessing / without auth', async ({ page }) => {
    // Clear any existing auth
    await page.evaluate(() => localStorage.clear())

    // Try to access chat page
    await page.goto('/')

    // Should redirect to login
    await expect(page).toHaveURL('/login')
    await expect(page.getByText('Login to your account')).toBeVisible()
  })
})
