/* eslint-disable testing-library/prefer-screen-queries */
import { test, expect } from '@playwright/test'
import fs from 'fs'

import { domain } from './utils'

const datasetName = `ui_test_dataset_${crypto.randomUUID().replace('-', '_').slice(0, 8)}`
const filePath = 'playwright/gapminder.csv'
const downloadPath = `playwright/.downloads/${datasetName}`

test('test', async ({ page }) => {
  await page.goto(domain)

  // Create a schema
  await page.getByRole('link', { name: 'Add New Dataset' }).click()
  await expect(page).toHaveURL(`${domain}/schema/create`)
  await page.locator('[data-testid="field-level"]').selectOption('PUBLIC')
  await page.locator('[data-testid="field-layer"]').selectOption('default')
  await page.locator('[data-testid="field-domain"]').click()
  await page.locator('[data-testid="field-domain"]').fill('ui_test_domain')
  await page.locator('[data-testid="field-title"]').click()
  await page.locator('[data-testid="field-title"]').fill(datasetName)
  await page.locator('[data-testid="field-file"]').setInputFiles(filePath)
  await page.locator('[data-testid="submit"]').click()
  await page.locator('input[name="ownerEmail"]').click()
  await page.locator('input[name="ownerEmail"]').fill('ui_test@email.com')
  await page.locator('input[name="ownerName"]').click()
  await page.locator('input[name="ownerName"]').fill('ui_test')
  await page.locator('button:has-text("Add Dataset")').click()
  const schemaCreatedElement = await page.waitForSelector('.MuiAlertTitle-root')
  expect(await schemaCreatedElement.innerText()).toEqual('Dataset added successfully')

  // Upload a dataset
  await page.goto(`${domain}/data/upload`)
  await page.getByTestId('select-layer').getByRole('combobox').click()
  await page.getByRole('option', { name: 'default' }).click()
  await page.getByTestId('select-domain').getByRole('combobox').click()
  await page.getByRole('option', { name: 'ui_test_domain' }).click()
  await page.getByTestId('select-dataset').getByRole('combobox').click()
  await page.getByRole('option', { name: datasetName }).click()
  await page.getByTestId('upload').setInputFiles(filePath)
  await page.getByTestId('submit').click()

  // Upload now redirects to the job detail page once processing completes
  await page.waitForURL(`${domain}/tasks/*`, { timeout: 30000 })
  expect(await page.getByText('Success').textContent()).toContain('Success')

  // Download the dataset
  await page.goto(`${domain}/data/download`)
  await page.getByTestId('select-layer').getByRole('combobox').click()
  await page.getByRole('option', { name: 'default' }).click()
  await page.getByTestId('select-domain').getByRole('combobox').click()
  await page.getByRole('option', { name: 'ui_test_domain' }).click()
  await page.getByTestId('select-dataset').getByRole('combobox').click()
  await page.getByRole('option', { name: datasetName }).click()
  await page.getByTestId('submit').click()

  const metadataTable = page.getByRole('table').first()
  expect((await metadataTable.innerText()).toLowerCase()).toContain('last uploaded by')
  const lastUploadedByValue = await page.getByRole('row', { name: /Last uploaded by/i }).locator('td').last().innerText()
  expect(lastUploadedByValue).not.toEqual('')

  await page.getByPlaceholder('30').fill('200')
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Download', exact: true }).click()
  const download = await downloadPromise
  await download.saveAs(downloadPath)

  expect(fs.existsSync(downloadPath)).toBeTruthy()

  fs.rm(downloadPath, (err) => {
    err ? console.error(err) : console.info('Download deleted')
  })

  // Search for dataset
  await page.getByRole('link', { name: 'Catalog' }).click()
  await expect(page).toHaveURL(`${domain}/catalog`)
  await page.getByPlaceholder('Search by dataset name…').click()
  await page.getByPlaceholder('Search by dataset name…').fill(datasetName)

  expect(await page.getByRole('table').innerText()).toContain(datasetName)

  // Delete the dataset
  await page.goto(`${domain}/data/delete`)
  await page.getByTestId('select-layer').getByRole('combobox').click()
  await page.getByRole('option', { name: 'default' }).click()
  await page.getByTestId('select-domain').getByRole('combobox').click()
  await page.getByRole('option', { name: 'ui_test_domain' }).click()
  await page.getByTestId('select-dataset').getByRole('combobox').click()
  await page.getByRole('option', { name: datasetName }).click()
  await page.getByTestId('submit').click()

  expect(await page.getByTestId('delete-status').innerText()).toEqual(
    `Dataset deleted: default/ui_test_domain/${datasetName}`
  )
})
