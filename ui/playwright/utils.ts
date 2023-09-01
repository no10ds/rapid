import { SecretsManager } from 'aws-sdk'

const client = new SecretsManager({ region: process.env.AWS_REGION })

const baseDomain = process.env.DOMAIN_NAME
export const domain = `https://${baseDomain.replace('/api', '')}`

export async function makeAPIRequest(
  path: string,
  method: string,
  body?: any,
  authToken?: string,
  optionalHeaders = {},
): Promise<any> {
  const response = await fetch(`https://${baseDomain}/${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...optionalHeaders,
      ...(authToken ? { Authorization: authToken } : {}),
    },
    body: JSON.stringify(body),
  })
  return response.json()
}

export async function getSecretValue(secretName: string): Promise<string | void> {
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

export async function generateRapidAuthToken(): Promise<any> {
  const secretName = `${process.env.RESOURCE_PREFIX}_E2E_TEST_CLIENT_USER_ADMIN`
  const clientId = JSON.parse((await getSecretValue(secretName)) as string)['CLIENT_ID']
  const clientSecret = JSON.parse((await getSecretValue(secretName)) as string)[
    'CLIENT_SECRET'
  ]
  const credentialsSecret = btoa(`${clientId}:${clientSecret}`)
  return makeAPIRequest(
    'oauth2/token',
    'POST',
    {
      grant_type: 'client_credentials',
      client_id: clientId,
    },
    `Basic ${credentialsSecret}`,
    {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  )
}
