FROM node:18 AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18 AS dev

WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY . .

ENV NODE_ENV=development
ENV HOST=0.0.0.0
ENV PORT=3000
ENV BASE_HOST=http://host.docker.internal:80

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM node:18-alpine AS prod

WORKDIR /app
COPY --from=builder /app/.output ./
COPY --from=builder /app/node_modules ./node_modules

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=80
ENV BASE_HOST=http://traefik:80

EXPOSE 80
CMD ["node", ".output/server/index.mjs"]