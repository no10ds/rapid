/* eslint-disable testing-library/prefer-screen-queries */
import { test, expect } from '@playwright/test'

import { makeAPIRequest, generateRapidAuthToken } from './utils'

const domain = 'http://localhost:3000'

const user = `${process.env.RESOURCE_PREFIX}_ui_test_user`

test('test', async ({ page }) => {
  await page.goto(domain)

  // Modify user to have data admin permissions
  await page.locator('div[role="button"]:has-text("Modify User")').click()
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
  await makeAPIRequest(
    'subjects/permissions',
    'PUT',
    {
      subject_id: 'b10ded88-4e10-46d3-b9c7-ff6cf0526c09',
      permissions: [
        'DATA_ADMIN',
        'READ_ALL',
        'USER_ADMIN',
        'WRITE_ALL',
        'READ_DEFAULT_PROTECTED_TEST_E2E_PROTECTED',
      ],
    },
    `Bearer ${access_token}`,
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
