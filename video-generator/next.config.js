/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  serverExternalPackages: ['@remotion/bundler', '@remotion/renderer'],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  webpack: (config, {  }) => {
    // Exclude TypeScript definition files from webpack processing
    config.module.rules.push({
      test: /\.d\.ts$/,
      use: 'ignore-loader'
    });
    
    // Add fallbacks for Node.js modules
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
      os: false,
    };
    
    // Fix for Remotion self-reference dependency issues
    config.ignoreWarnings = [
      {
        module: /node_modules\/@remotion/,
        message: /Self-reference dependency has unused export name/,
      },
    ];
    
    // Additional webpack optimization for Remotion
    config.optimization = {
      ...config.optimization,
      sideEffects: false,
    };
    
    return config;
  },
};

module.exports = nextConfig;
