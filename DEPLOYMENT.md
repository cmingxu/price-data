# Docker Deployment Guide

## Overview

This project uses Docker Compose to deploy two services:
- **API Service**: Runs the FastAPI server on port 8000
- **Scraper Service**: Runs daily data scraping at 3:00 AM Beijing time

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- At least 1GB free disk space

### 2. Environment Setup

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` file if needed (default values should work for Docker deployment).

### 3. Deploy Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the API

- API: http://localhost:8000
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

## Service Details

### API Service
- **Container**: `price-data-api`
- **Port**: 8000
- **Health Check**: Automatic health monitoring
- **Restart Policy**: Unless stopped manually

### Scraper Service
- **Container**: `price-data-scraper`
- **Schedule**: Daily at 3:00 AM Beijing time
- **Timezone**: Asia/Shanghai
- **Logs**: `/var/log/scraper.log` and `/var/log/cron.log`

## Management Commands

```bash
# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View API logs
docker-compose logs api

# View scraper logs
docker-compose logs scraper

# Execute manual scraping
docker-compose exec scraper python scheduler.py

# Access API container shell
docker-compose exec api bash

# Access scraper container shell
docker-compose exec scraper bash
```

## Data Persistence

- **Database**: Stored in `./data/price_data.db`
- **Logs**: Stored in `./logs/` directory
- **Volumes**: Automatically created and managed by Docker Compose

## Monitoring

### Health Checks
- API service has built-in health monitoring
- Unhealthy containers will be automatically restarted

### Log Monitoring
```bash
# Real-time log monitoring
docker-compose logs -f

# Check scraper cron logs
docker-compose exec scraper tail -f /var/log/cron.log

# Check scraper application logs
docker-compose exec scraper tail -f /var/log/scraper.log
```

## Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Database permission issues**
   ```bash
   # Fix data directory permissions
   sudo chown -R $USER:$USER ./data
   ```

3. **Scraper not running**
   ```bash
   # Check cron service status
   docker-compose exec scraper service cron status
   
   # Manually trigger scraping
   docker-compose exec scraper python scheduler.py
   ```

4. **View container resource usage**
   ```bash
   docker stats
   ```

### Debug Mode

```bash
# Run services in foreground with debug output
docker-compose up

# Rebuild containers after code changes
docker-compose up --build
```

## Production Considerations

1. **Security**
   - Change default database location
   - Use environment-specific `.env` files
   - Consider using Docker secrets for sensitive data

2. **Backup**
   ```bash
   # Backup database
   cp ./data/price_data.db ./backups/price_data_$(date +%Y%m%d).db
   ```

3. **Monitoring**
   - Set up log aggregation (ELK stack, etc.)
   - Monitor container health and resource usage
   - Set up alerts for scraping failures

4. **Scaling**
   - API service can be scaled horizontally
   - Use load balancer for multiple API instances
   - Consider using external database for production

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/price_data.db` | Database connection string |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `TZ` | `Asia/Shanghai` | Timezone for scraper |

### Customizing Schedule

To change the scraping schedule, edit the `crontab` file:
```bash
# Example: Run every 6 hours
0 */6 * * * cd /app && python scheduler.py >> /var/log/cron.log 2>&1
```

Then rebuild the scraper container:
```bash
docker-compose up --build scraper
```