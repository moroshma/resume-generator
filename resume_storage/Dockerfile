FROM golang:latest AS builder
WORKDIR /app

# Copy go mod files
COPY resume_storage/go.mod resume_storage/go.sum ./

# Copy user_service directory
COPY user_service/ ./user_service/

# Download dependencies
RUN go mod download

# Copy source code
COPY resume_storage/ ./resume_storage

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./cmd/main.go

# Final stage
FROM alpine:latest
WORKDIR /app

# Copy the binary from builder
COPY --from=builder /app/main .
COPY --from=builder /app/config ./config

# Expose port
EXPOSE 8100

# Run the application
CMD ["./main"]
