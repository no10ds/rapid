import { test as setup, expect } from '@playwright/test'
import { domain, getSecretValue } from './utils'

const authFile = 'playwright/.auth/user.json'
const secretName = `${process.env.RESOURCE_PREFIX}_UI_TEST_USER`

setup('authenticate', async ({ page }) => {
  const secret = JSON.parse((await getSecretValue(secretName)) as string)
  await page.goto(domain)
  await page.goto(`${domain}/login`)

  await page.locator('[data-testid="login-link"]').click()

  await page.locator('[placeholder="Username"]').nth(1).click()

  await page.locator('[placeholder="Password"]').nth(1).click()

  await page.locator('[placeholder="Password"]').nth(1).fill(`${secret['password']}`)

  await page.locator('[placeholder="Username"]').nth(1).click()

  await page.locator('[placeholder="Username"]').nth(1).click()

  await page.locator('[placeholder="Username"]').nth(1).fill(`${secret['username']}`)

  await page.locator('text=Sign in').nth(3).click()
  await expect(page).toHaveURL(domain)

  await page.context().storageState({ path: authFile })
})
