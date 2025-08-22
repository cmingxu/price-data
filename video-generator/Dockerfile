# Use Node.js 18 LTS as base image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Update apt sources and install system dependencies for video processing
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    chromium \
    fonts-liberation \
    fonts-noto-cjk \
    fonts-wqy-zenhei \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set Puppeteer to use installed Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create output directory
RUN mkdir -p output

# Expose port
EXPOSE 3002

# Set default command
CMD ["npm", "run", "dev"]