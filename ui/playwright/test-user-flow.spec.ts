import { test, expect } from '@playwright/test';

const domain = process.env.DOMAIN;
const user = `${process.env.RESOURCE_PREFIX}_ui_test_user`

test('test', async ({ page }) => {
  await page.goto(domain);

  // Click div[role="button"]:has-text("Modify User")
  await page.locator('div[role="button"]:has-text("Modify User")').click();
  await expect(page).toHaveURL(`${domain}/subject/modify`);

  await page.locator('[data-testid="field-user"]').selectOption({ 'label': user })
  await page.locator('[data-testid="submit-button"]').click();

  await page.getByRole('row', { name: 'DATA_ADMIN' }).getByRole('button').click();
  await page.getByTestId('select-type').selectOption('DATA_ADMIN');
  await page.getByRole('row').filter({ hasText: 'ActionDATA_ADMIN' }).getByRole('button').click();
  await page.getByTestId('submit').click();
  await expect(page).toHaveURL(/success/);
});