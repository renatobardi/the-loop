# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM deps AS build
COPY . .
RUN npm run build
RUN npm ci --omit=dev

# Stage 3: Runner
FROM node:22-alpine AS runner
RUN apk upgrade --no-cache && \
    rm -rf /usr/local/lib/node_modules/npm /usr/local/bin/npm /usr/local/bin/npx && \
    addgroup -S nodejs && adduser -S sveltekit -u 1001 -G nodejs
WORKDIR /app
COPY --from=build --chown=sveltekit:nodejs /app/build ./build
COPY --from=build --chown=sveltekit:nodejs /app/node_modules ./node_modules
COPY --from=build --chown=sveltekit:nodejs /app/package.json ./package.json
USER sveltekit
EXPOSE 3000
ENV PORT=3000
ENV NODE_ENV=production
CMD ["node", "build/index.js"]
