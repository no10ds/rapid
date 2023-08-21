import { test, expect } from '@playwright/test';

const domain = process.env.DOMAIN

test('test', async ({ page }) => {
  await page.goto(domain);
  await page.getByRole('button', { name: 'Create User' }).click();
  await page.getByRole('button', { name: 'Modify User' }).click();
  await page.getByRole('button', { name: 'Download data' }).click();
  await page.getByRole('button', { name: 'Upload data' }).click();
  await page.getByRole('button', { name: 'Create Schema' }).click();
  await page.getByRole('button', { name: 'Task Status' }).click();
  await page.getByRole('link', { name: 'Home' }).click();
  await page.getByRole('link', { name: 'Create User' }).nth(1).click();
  await page.getByRole('link', { name: 'Home' }).click();
  await page.getByRole('button', { name: 'account of current user' }).click();
  await page.getByText('Logout').click();
});