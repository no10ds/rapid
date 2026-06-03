/* eslint-disable testing-library/prefer-screen-queries */
import { test, expect } from '@playwright/test'

import { makeAPIRequest, generateRapidAuthToken, domain } from './utils'

const user = `${process.env.E2E_RESOURCE_PREFIX}_ui_test_user`

test('test', { timeout: 60000 }, async ({ page }) => {
  await page.goto(`${domain}/subject/modify`)

  // Modify user to have data admin permissions
  await expect(page).toHaveURL(`${domain}/subject/modify`)
  await page.locator('[data-testid="field-user"]').selectOption({ label: user })
  await page.locator('[data-testid="submit-button"]').click()
  await page.locator('.MuiSelect-select').click()
  await page.getByRole('option', { name: 'DATA_ADMIN', exact: true }).click()
  await page.getByTestId('add-permission').click()
  await page.getByTestId('submit').click()
  // await expect(page).toHaveURL(/success/)

  // Test unique condition where we correctly display permissions when modifying a user
  // even though they might have conflicting permissions within the filtering logic
  const { access_token } = await generateRapidAuthToken()
  const url = page.url()
  let subjectId = url.split('/').pop()
  subjectId = subjectId.split('?')[0]
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
  await page.goto(`${domain}/subject/modify`)
  await expect(page).toHaveURL(`${domain}/subject/modify`)
  await page.locator('[data-testid="field-user"]').selectOption({ label: user })
  await page.locator('[data-testid="submit-button"]').click()
  await page
    .getByRole('row')
    .filter({ hasText: 'TEST_E2E_PROTECTED' })
    .getByRole('button', { name: 'Remove' })
    .waitFor({ timeout: 30000 })
  await page
    .getByRole('row')
    .filter({ hasText: 'TEST_E2E_PROTECTED' })
    .getByRole('button', { name: 'Remove' })
    .click()
  await page.getByTestId('submit').click()
})
