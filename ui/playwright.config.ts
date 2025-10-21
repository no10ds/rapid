import { defineConfig, devices } from '@playwright/test'
import dotenv from 'dotenv'
import path from 'path'

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') })

const authFile = path.join(__dirname, 'playwright/.auth/user.json')

export default defineConfig({
  projects: [
    // Setup project
    { name: 'setup', testMatch: 'auth.setup.ts' },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Use prepared auth state.
        storageState: authFile
      },
      dependencies: ['setup']
    }
  ]
})
