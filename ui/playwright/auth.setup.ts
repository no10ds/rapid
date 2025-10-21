import { test as setup, expect } from '@playwright/test'
import { domain, getSecretValue } from './utils'
import * as fs from 'fs'
import * as path from 'path'

const authFile = 'playwright/.auth/user.json'
const secretName = `${process.env.E2E_RESOURCE_PREFIX}_UI_TEST_USER`

setup('authenticate', async ({ page }) => {
  console.log('[AUTH SETUP] Starting authentication process')
  console.log('[AUTH SETUP] Domain:', domain)
  console.log('[AUTH SETUP] Auth file path:', authFile)
  console.log('[AUTH SETUP] Resolved auth file path:', path.resolve(authFile))
  console.log('[AUTH SETUP] Current working directory:', process.cwd())

  const secret = JSON.parse((await getSecretValue(secretName)) as string)
  console.log('[AUTH SETUP] Retrieved secret for user:', secret['username'])

  await page.goto(domain)
  await page.goto(`${domain}/login`)
  console.log('[AUTH SETUP] Navigated to login page')

  await page.locator('[data-testid="login-link"]').click()
  console.log('[AUTH SETUP] Clicked login link')

  await page.locator('[placeholder="Username"]').nth(1).click()

  await page.locator('[placeholder="Password"]').nth(1).click()

  await page.locator('[placeholder="Password"]').nth(1).fill(`${secret['password']}`)
  console.log('[AUTH SETUP] Filled password')

  await page.locator('[placeholder="Username"]').nth(1).click()

  await page.locator('[placeholder="Username"]').nth(1).click()

  await page.locator('[placeholder="Username"]').nth(1).fill(`${secret['username']}`)
  console.log('[AUTH SETUP] Filled username')

  await page.locator('text=Sign in').nth(3).click()
  console.log('[AUTH SETUP] Clicked sign in')

  await expect(page).toHaveURL(domain)
  console.log('[AUTH SETUP] Successfully authenticated, now at:', page.url())

  // Get cookies before saving
  const cookies = await page.context().cookies()
  console.log('[AUTH SETUP] Number of cookies:', cookies.length)
  console.log('[AUTH SETUP] Cookie domains:', [...new Set(cookies.map(c => c.domain))])

  await page.context().storageState({ path: authFile })
  console.log('[AUTH SETUP] Saved storage state to:', authFile)

  // Verify file was created
  const resolvedPath = path.resolve(authFile)
  if (fs.existsSync(resolvedPath)) {
    const stats = fs.statSync(resolvedPath)
    console.log('[AUTH SETUP] ✓ Auth file created successfully')
    console.log('[AUTH SETUP] File size:', stats.size, 'bytes')
    console.log('[AUTH SETUP] File location:', resolvedPath)
  } else {
    console.error('[AUTH SETUP] ✗ Auth file was NOT created at:', resolvedPath)
  }
})
