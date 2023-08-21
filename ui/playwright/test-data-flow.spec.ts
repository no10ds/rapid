import { test, expect } from '@playwright/test';
import { v4 } from 'uuid';
import fs from 'fs';

const domain = process.env.DOMAIN;
const datasetName = `ui_test_dataset_${v4().replace('-', '_').slice(0, 8)}`
const filePath = 'playwright/gapminder.csv'
const downloadPath = `playwright/.downloads/${datasetName}`

test('test', async ({ page }) => {
    await page.goto(domain);

    // Create a schema
    await page.locator('div[role="button"]:has-text("Create Schema")').click();
    await expect(page).toHaveURL(`${domain}/schema/create`);
    await page.locator('[data-testid="field-level"]').selectOption('PUBLIC');
    await page.locator('[data-testid="field-layer"]').selectOption('default');
    await page.locator('[data-testid="field-domain"]').click();
    await page.locator('[data-testid="field-domain"]').fill('ui_test_domain');
    await page.locator('[data-testid="field-title"]').click();
    await page.locator('[data-testid="field-title"]').fill(datasetName);
    await page.locator('[data-testid="field-file"]').click();
    await page.locator('[data-testid="field-file"]').setInputFiles(filePath);
    await page.locator('[data-testid="submit"]').click();
    await page.locator('input[name="ownerEmail"]').click();
    await page.locator('input[name="ownerEmail"]').fill('ui_test@email.com');
    await page.locator('input[name="ownerName"]').click();
    await page.locator('input[name="ownerName"]').fill('ui_test');
    await page.locator('button:has-text("Create Schema")').click();
    // @ts-ignore
    const schemaCreatedElement = await page.waitForSelector('.MuiAlertTitle-root', { text: 'Schema Created' });

    expect(await schemaCreatedElement.innerText()).toEqual('Schema Created');

    // Upload a dataset
    await page.getByRole('button', { name: 'Upload data' }).click();
    await page.getByTestId('select-layer').getByRole('combobox').click();
    await page.getByRole('option', { name: 'default' }).click();
    await page.getByTestId('select-domain').getByRole('combobox').click();
    await page.getByRole('option', { name: 'ui_test_domain' }).click();
    await page.getByTestId('select-dataset').getByRole('combobox').click();
    await page.getByRole('option', { name: datasetName }).click();
    await page.getByTestId('upload').click();
    await page.getByTestId('upload').setInputFiles(filePath);
    await page.getByTestId('submit').click();

    expect(await page.getByText('Data uploaded successfully').textContent()).toEqual('Status: Data uploaded successfully')

    // Download the dataset
    await page.getByRole('button', { name: 'Download data' }).click();
    await page.getByTestId('select-layer').getByRole('combobox').click();
    await page.getByRole('option', { name: 'default' }).click();
    await page.getByTestId('select-domain').getByRole('combobox').click();
    await page.getByRole('option', { name: 'ui_test_domain' }).click();
    await page.getByTestId('select-dataset').getByRole('combobox').click();
    await page.getByRole('option', { name: datasetName }).click();
    await page.getByTestId('submit').click();
    await page.locator('div').filter({ hasText: 'Row Limit' }).locator('div').nth(1).click();
    await page.getByPlaceholder('30').fill('200');
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download', exact: true }).click();
    const download = await downloadPromise;
    await download.saveAs(downloadPath)

    expect(fs.existsSync(downloadPath)).toBeTruthy()

    fs.rm(downloadPath, (err) => {
        err ? console.error(err) : console.log("Download deleted")
    })

    // Delete the dataset
    await page.getByRole('button', { name: 'Delete data' }).click();
    await page.locator('div[role="button"]:has-text("Delete data")').click();
    await page.getByTestId('select-layer').getByRole('combobox').click();
    await page.getByRole('option', { name: 'default' }).click();
    await page.getByTestId('select-domain').getByRole('combobox').click();
    await page.getByRole('option', { name: 'ui_test_domain' }).click();
    await page.getByTestId('select-dataset').getByRole('combobox').click();
    await page.getByRole('option', { name: datasetName }).click();
    await page.getByTestId('submit').click();

    // @ts-ignore
    const datasetDeletedElement = await page.waitForSelector('.MuiAlertTitle-root', { text: `Dataset deleted: default/ui_test_domain/${datasetName}` });

    expect(await datasetDeletedElement.innerText()).toEqual(`Dataset deleted: default/ui_test_domain/${datasetName}`);

});