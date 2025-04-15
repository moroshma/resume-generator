FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY --from=builder /app/.output ./.output

RUN addgroup -g 1001 nuxtuser && \
    adduser -u 1001 -G nuxtuser -D nuxtuser
USER nuxtuser

EXPOSE 3000
ENV NUXT_HOST=0.0.0.0
CMD ["node", ".output/server/index.mjs"]