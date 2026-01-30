import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager'

const client = new SecretsManagerClient({ region: process.env.AWS_REGION })

export const domain = `https://${process.env.E2E_DOMAIN_NAME.replace('/api', '')}`

export async function makeAPIRequest(
  path: string,
  method: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  body?: any,
  authToken?: string,
  optionalHeaders = {}
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
): Promise<any> {
  const response = await fetch(`${domain}/api/${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...optionalHeaders,
      ...(authToken ? { Authorization: authToken } : {})
    },
    body: JSON.stringify(body)
  })
  return await response.json()
}

export async function getSecretValue(secretName: string): Promise<string | undefined> {
  try {
    const command = new GetSecretValueCommand({ SecretId: secretName })
    const data = await client.send(command)
    return data.SecretString
  } catch (err) {
    throw err
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function generateRapidAuthToken(): Promise<any> {
  const secretName = `${process.env.E2E_RESOURCE_PREFIX}_E2E_TEST_CLIENT_USER_ADMIN`
  const clientId = JSON.parse((await getSecretValue(secretName)) as string)['CLIENT_ID']
  const clientSecret = JSON.parse((await getSecretValue(secretName)) as string)[
    'CLIENT_SECRET'
  ]
  const credentialsSecret = btoa(`${clientId}:${clientSecret}`)
  return await makeAPIRequest(
    'oauth2/token',
    'POST',
    {
      grant_type: 'client_credentials',
      client_id: clientId
    },
    `Basic ${credentialsSecret}`,
    {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  )
}
