import type { NextApiRequest, NextApiResponse } from 'next'
import type { AccessTokenResponse } from '@/service/types'

const generateToken = async () => {
  const auth = Buffer.from(
    `${process.env.UI_CLIENT_ID}:${process.env.UI_CLIENT_SECRET}`
  ).toString('base64')
  const headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    Authorization: `Basic ${auth}`
  }
  const data = {
    grant_type: 'client_credentials',
    client_id: process.env.UI_CLIENT_ID
  }
  const url = `${process.env.NEXT_PUBLIC_API_URL_PROXY}/api/oauth2/token`
  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  })

  return await response.json()
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<AccessTokenResponse>
) {
  const responseData = await generateToken()
  res.status(200).json({ token: responseData.access_token })
}
