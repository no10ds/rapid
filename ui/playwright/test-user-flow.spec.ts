/* eslint-disable testing-library/prefer-screen-queries */
import { test, expect } from '@playwright/test'

import { makeAPIRequest, generateRapidAuthToken, domain } from './utils'

const user = `${process.env.E2E_RESOURCE_PREFIX}_ui_test_user`

test('test', async ({ page }) => {
  await page.goto(domain)

  // Modify user to have data admin permissions
  https: await page.locator('div[role="button"]:has-text("Modify User")').click()
  await expect(page).toHaveURL(`${domain}/subject/modify`)
  await page.locator('[data-testid="field-user"]').selectOption({ label: user })
  await page.locator('[data-testid="submit-button"]').click()
  await page.getByRole('row', { name: 'DATA_ADMIN' }).getByRole('button').click()
  await page.getByTestId('select-type').selectOption('DATA_ADMIN')
  await page
    .getByRole('row')
    .filter({ hasText: 'ActionDATA_ADMIN' })
    .getByRole('button')
    .click()
  await page.getByTestId('submit').click()
  // await expect(page).toHaveURL(/success/)

  // Test unique condition where we correctly display permissions when modifying a user
  // even though they might have conflicting permissions within the filtering logic
  const { access_token } = await generateRapidAuthToken()
  const url = new URL(page.url())
  const subjectId = url.pathname.split('/').pop()
  await makeAPIRequest(
    'subjects/permissions',
    'PUT',
    {
      subject_id: subjectId,
      permissions: [
        'DATA_ADMIN',
        'READ_ALL',
        'USER_ADMIN',
        'WRITE_ALL',
        'READ_DEFAULT_PROTECTED_TEST_E2E_PROTECTED'
      ]
    },
    `Bearer ${access_token}`
  )
  await page.locator('div[role="button"]:has-text("Modify User")').click()
  await expect(page).toHaveURL(`${domain}/subject/modify`)
  await page.locator('[data-testid="field-user"]').selectOption({ label: user })
  await page.locator('[data-testid="submit-button"]').click()
  await page
    .getByRole('row', { name: 'READ DEFAULT PROTECTED TEST_E2E_PROTECTED' })
    .getByRole('button')
    .click()
  await page.getByTestId('submit').click()
})
