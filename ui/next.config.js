const apiProx = process.env.NEXT_PUBLIC_API_URL_PROXY || null
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: false,
  swcMinify: true,
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/,
      use: [{ loader: '@svgr/webpack', options: { icon: true } }]
    })
    return config
  },
  images: {
    unoptimized: true
  },
  async rewrites() {
    return process.env.NODE_ENV === 'development' && !!apiProx
      ? [
          {
            source: process.env.NEXT_PUBLIC_API_URL + '/:path*',
            destination: apiProx + '/:path*'
          }
        ]
      : []
  }
}

module.exports = nextConfig
