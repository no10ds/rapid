/* eslint-disable testing-library/prefer-screen-queries */
import { test, expect } from '@playwright/test'

import { domain } from './utils'

const user = `${process.env.E2E_RESOURCE_PREFIX}_ui_test_user`

// Read-only walk through the User Admin area. Mutating permissions is covered by
// the subject unit tests; here we only verify the real-backend navigation:
// User Admin table -> search -> open a subject -> its permissions render.
test('test', async ({ page }) => {
  await page.goto(`${domain}/subject`)
  await expect(page).toHaveURL(`${domain}/subject`)

  await page.getByPlaceholder('Search by name…').fill(user)

  const row = page.getByRole('row').filter({ hasText: user }).first()
  await expect(row).toBeVisible()
  await row.click()

  await page.waitForURL(`${domain}/subject/modify/*`)
  await expect(page.getByText(`Edit permissions — ${user}`)).toBeVisible()
  await expect(page.getByRole('columnheader', { name: 'Type' })).toBeVisible()
})
