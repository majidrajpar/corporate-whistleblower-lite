FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (prisma is needed for generate)
RUN npm ci

# Copy source code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Generate Prisma client
RUN npx prisma generate

# Expose port
EXPOSE 3001

# Start server
CMD ["npm", "start"]
