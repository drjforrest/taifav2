import type { NextConfig } from "next";

/**
 * Next.js Configuration with Turbopack Compatibility
 * 
 * This config automatically detects if running with Turbopack (--turbo flag)
 * and conditionally applies webpack-specific configurations only when needed.
 * 
 * Usage:
 * - `npm run dev` - Uses Turbopack (faster, experimental)
 * - `npm run dev:webpack` - Uses traditional webpack (stable)
 * - `npm run build` - Always uses webpack for production builds
 */

// Check if running with Turbopack
const usingTurbopack = process.argv.includes('--turbo');

// Log the current mode for clarity
if (process.env.NODE_ENV === 'development') {
  console.log(`🚀 Next.js running with ${usingTurbopack ? 'Turbopack' : 'Webpack'}`);
}

// Base configuration that works for both webpack and Turbopack
const baseConfig: NextConfig = {
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
};

// Webpack-specific configuration
const webpackConfig = {
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
};

// Turbopack-specific configuration
const turbopackConfig = {
  experimental: {
    ...baseConfig.experimental,
    turbo: {
      rules: {
        // Optimize CSS processing
        '*.css': ['css-loader'],
        // Optimize TypeScript compilation
        '*.{ts,tsx}': ['swc-loader'],
      },
    },
  },
};

// Combine configurations based on bundler
const nextConfig: NextConfig = usingTurbopack 
  ? { ...baseConfig, ...turbopackConfig }
  : { ...baseConfig, ...webpackConfig };

export default nextConfig;
