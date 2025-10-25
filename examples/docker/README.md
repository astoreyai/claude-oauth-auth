# Docker Deployment Example

Containerized application demonstrating Claude API integration in Docker with proper configuration, health checks, and best practices.

## Features

- Multi-stage Docker build
- Environment configuration
- Health checks
- Resource limits
- Non-root user security
- Docker Compose orchestration

## Quick Start

1. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN
   ```

2. **Build and run:**
   ```bash
   docker-compose up --build
   ```

3. **Test:**
   ```bash
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/api/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello Claude!"}'
   ```

## Docker Commands

### Build Image
```bash
docker build -t claude-oauth-demo .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your-key" \
  claude-oauth-demo
```

### Using Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up --build
```

## Configuration

### Environment Variables

Set in `.env` file or `docker-compose.yml`:

```env
# Authentication (choose one)
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_AUTH_TOKEN=sk-ant-oat01-...

# Application
API_HOST=0.0.0.0
API_PORT=8000
```

### Volume Mounting

To use Claude Code OAuth credentials:

```yaml
volumes:
  - ~/.claude/.credentials.json:/root/.claude/.credentials.json:ro
```

## Health Checks

The container includes health checks:

```bash
# Check container health
docker ps

# Manual health check
curl http://localhost:8000/health
```

## Production Deployment

### Use Production Server

Modify `Dockerfile` to use Gunicorn:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

### Security Best Practices

1. **Use secrets management:**
   ```bash
   docker secret create anthropic_key /path/to/key
   ```

2. **Run as non-root user:**
   Already configured in Dockerfile

3. **Limit resources:**
   Set in docker-compose.yml

4. **Use HTTPS:**
   Deploy behind reverse proxy (nginx, traefik)

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs claude-app
```

### Authentication errors

Verify environment variables:
```bash
docker-compose exec claude-app env | grep ANTHROPIC
```

### Health check failing

Check health status:
```bash
docker inspect --format='{{json .State.Health}}' claude-oauth-demo
```

## License

MIT License - see main package for details.
