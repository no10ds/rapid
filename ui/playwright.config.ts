import { defineConfig, devices } from '@playwright/test'
import dotenv from 'dotenv'
import path from 'path'

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') })

const authFile = 'playwright/.auth/user.json'
const resolvedAuthPath = path.resolve(authFile)

console.log('[PLAYWRIGHT CONFIG] Auth file path:', authFile)
console.log('[PLAYWRIGHT CONFIG] Resolved path:', resolvedAuthPath)
console.log('[PLAYWRIGHT CONFIG] Current working directory:', process.cwd())
console.log('[PLAYWRIGHT CONFIG] Config file location:', __dirname)

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
