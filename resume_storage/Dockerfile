FROM golang:latest AS builder
WORKDIR /app

# Копируем весь проект
COPY . .

# Переходим в директорию с go.mod
WORKDIR /app/resume_storage

# Загружаем зависимости
RUN go mod download

# Собираем приложение
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./cmd/main.go

# Финальный этап
FROM alpine:latest
WORKDIR /app

# Копируем бинарник из builder
COPY --from=builder /app/resume_storage/main .

# Копируем конфигурацию, если она есть
COPY --from=builder /app/resume_storage/config ./config

# Экспортируем порт
EXPOSE 8100

# Запускаем приложение
CMD ["./main"]