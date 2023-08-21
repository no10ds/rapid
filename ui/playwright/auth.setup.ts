import { test as setup, expect } from '@playwright/test';
import { SecretsManager } from 'aws-sdk'

const client = new SecretsManager({ region: process.env.AWS_REGION })
const authFile = 'playwright/.auth/user.json';
const domain = process.env.DOMAIN;
const secretName = `${process.env.RESOURCE_PREFIX}_UI_TEST_USER`


export async function getSecretValue(
    secretName: string
): Promise<string | void> {
    return new Promise((resolve, reject) => {
        client.getSecretValue({ SecretId: secretName }, function (err, data) {
            if (err) {
                reject(err)
            } else {
                resolve(data.SecretString)
            }
        })
    })
}


setup('authenticate', async ({ page }) => {
    const secret = JSON.parse(await getSecretValue(secretName) as string)
    await page.goto(domain);
    await page.goto(`${domain}/login`);

    await page.locator('[data-testid="login-link"]').click();

    await page.locator('[placeholder="Username"]').nth(1).click();

    await page.locator('[placeholder="Password"]').nth(1).click();

    await page.locator('[placeholder="Password"]').nth(1).fill(`${secret['password']}`);

    await page.locator('[placeholder="Username"]').nth(1).click();

    await page.locator('[placeholder="Username"]').nth(1).click();

    await page.locator('[placeholder="Username"]').nth(1).fill(`${secret['username']}`);

    await page.locator('text=Sign in').nth(3).click();
    await expect(page).toHaveURL(domain);

    await page.context().storageState({ path: authFile });
});