import type { NextConfig } from "next";

/**
 * Next.js Configuration
 * Optimized for both development and production with webpack customizations
 */

const nextConfig: NextConfig = {
  // Ensure proper static file handling
  output: 'standalone',
  
  // Optimize for production
  compress: true,
  
  // Ensure proper asset prefix for production
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
  
  // Optimize resource hints and preloading
  experimental: {
    optimizePackageImports: ['react-tabs', 'lucide-react'],
  },
  
  // Add headers for better resource loading
  async headers() {
    return [
      {
        source: '/_next/static/css/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  
  // Webpack configuration - only apply for production builds
  ...(process.env.NODE_ENV === 'production' && {
    webpack: (config: any, { dev, isServer }: { dev: boolean; isServer: boolean }) => {
      if (!dev && !isServer) {
        // Ensure consistent chunk naming
        config.optimization.splitChunks = {
          ...config.optimization.splitChunks,
          cacheGroups: {
            ...config.optimization.splitChunks.cacheGroups,
            // Separate CSS from vendor chunks to reduce preload warnings
            styles: {
              name: 'styles',
              test: /\.(css|scss|sass)$/,
              chunks: 'all',
              priority: 20,
              reuseExistingChunk: true,
              enforce: true,
            },
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
              priority: 10,
            },
            default: {
              minChunks: 2,
              priority: -20,
              reuseExistingChunk: true,
            },
          },
        };
      }
      return config;
    },
  }),
};

export default nextConfig;
