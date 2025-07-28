/** @type {import('next').NextConfig} */
const nextConfig = {
    // Add this rewrites configuration
    async rewrites() {
        return [
            {
                source: "/api/:path*",
                destination: "http://localhost:8000/api/:path*",
            },
        ];
    },
};

export default nextConfig;