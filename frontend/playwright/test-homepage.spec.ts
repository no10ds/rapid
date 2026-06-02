/* eslint-disable testing-library/prefer-screen-queries */
import { test, expect } from '@playwright/test'

import { domain } from './utils'

test('test', async ({ page }) => {
  await page.goto(domain)

  await page.getByRole('link', { name: 'Catalog' }).click()
  await expect(page).toHaveURL(`${domain}/catalog`)

  await page.getByRole('link', { name: 'Add Dataset' }).click()
  await expect(page).toHaveURL(`${domain}/schema/create`)

  await page.getByRole('link', { name: 'Jobs' }).click()
  await expect(page).toHaveURL(`${domain}/tasks`)

  await page.getByRole('link', { name: 'User Admin' }).click()
  await expect(page).toHaveURL(`${domain}/subject`)

  await page.locator('.MuiAvatar-root').click()
  await page.getByRole('menuitem', { name: 'Sign out' }).click()
})
