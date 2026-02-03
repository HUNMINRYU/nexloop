import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
    distDir: 'dist',
    images: {
        unoptimized: true,
    },
    webpack: (config, { dev }) => {
        if (dev) {
            config.watchOptions = {
                ignored: ['**/node_modules', '**/dist', '**/.git'],
            };
        }
        return config;
    },
};

export default nextConfig;
