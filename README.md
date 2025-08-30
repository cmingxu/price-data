# Price Data System

A comprehensive system for scraping agricultural product price data from Xinfadi market, with automated data processing and video generation capabilities.

## Demo

[Click to watch demo](https://raw.githubusercontent.com/cmingxu/price-data/main/)

## 🏗️ Project Structure

This project consists of two main components:

### 1. Price Data Scraper & API
A Python-based system that scrapes price data from Xinfadi market and provides RESTful API access.

### 2. Video Generator
A Next.js application that generates promotional videos using the scraped price data with Remotion.

## 🚀 Features

### Data Scraping System
- **Automated Scraping**: Continuous data collection every 3 hours using a busy loop scheduler
- **Data Management**: SQLAlchemy + MySQL storage with deduplication and incremental sync
- **RESTful API**: Complete CRUD operations with FastAPI
- **Statistical Analysis**: Built-in data analytics and trending calculations
- **Robust Logging**: Multi-level logging system with rotation

### Video Generator
- **Dynamic Video Creation**: Generates videos from price data using Remotion
- **Background Music**: Continuous BGM playback throughout video duration
- **Customizable Templates**: Support for different product categories (vegetables, fruits)
- **Modern UI**: Beautiful and responsive web interface
- **Export Options**: High-quality MP4 video output

## 🛠️ Technology Stack

### Backend
- **Python 3.12**: Core language
- **FastAPI**: Web framework for API
- **SQLAlchemy**: ORM for database operations
- **MySQL**: Primary database
- **Docker**: Containerization
- **Loguru**: Advanced logging

### Frontend & Video Generation
- **Next.js 14**: React framework
- **TypeScript**: Type-safe development
- **Remotion**: Video generation framework
- **Tailwind CSS**: Styling framework
- **Docker**: Containerized deployment

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.12+ (for local development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd price-data
```

### 2. Environment Setup

```bash
# Copy environment templates
cp .env.example .env
cp video-generator/.env.example video-generator/.env
```

### 3. Configure Environment Variables

Edit `.env` file:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/price_data
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 4. Start with Docker Compose

```bash
# Start all services
docker compose up -d

# Or start individual services
docker compose up api -d      # API server
docker compose up scraper -d  # Data scraper
```

### 5. Access the Applications

- **API Documentation**: http://localhost:8000/docs
- **Video Generator**: http://localhost:3000
- **API Health Check**: http://localhost:8000/health

## 📊 API Endpoints

### Price Data
- `GET /api/prices` - List price data with filtering
- `GET /api/prices/{id}` - Get specific price record
- `POST /api/prices` - Create new price record
- `PUT /api/prices/{id}` - Update price record
- `DELETE /api/prices/{id}` - Delete price record

### Data Synchronization
- `POST /api/sync` - Manual data sync
- `POST /api/sync/incremental` - Incremental sync
- `GET /api/sync/status` - Sync status

### Analytics
- `GET /api/statistics` - Data statistics
- `GET /api/trending` - Trending analysis
- `GET /api/products` - Product list
- `GET /api/categories` - Category list

### System
- `GET /health` - Health check
- `GET /api/logs` - System logs

## 🎥 Video Generation

The video generator creates dynamic promotional videos from price data:

### Features
- **Title Page**: Animated introduction with category information
- **Data Pages**: Paginated price data display (15 items per page)
- **Ending Page**: Professional closing with branding
- **Background Music**: Continuous audio throughout the video
- **Responsive Design**: Adapts to different data volumes

### Usage

1. Access the video generator at http://localhost:3000
2. Select product category (vegetables, fruits, etc.)
3. Configure video parameters
4. Generate and download the video

### Video Specifications
- **Resolution**: 1080p (1920x1080)
- **Frame Rate**: 30 FPS
- **Format**: MP4
- **Duration**: Dynamic based on data volume
- **Audio**: Background music with seamless looping

## 🔧 Development

### Local Development Setup

#### Backend Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python main.py init

# Start development server
python main.py server --reload
```

#### Frontend Development
```bash
cd video-generator

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd video-generator
npm test
```

## 📦 Deployment

### Production Deployment

```bash
# Build and deploy all services
docker compose -f docker-compose.prod.yml up -d
```

### Individual Service Deployment

```bash
# Deploy API only
docker compose up api -d

# Deploy scraper only
docker compose up scraper -d

# Deploy video generator
cd video-generator
npm run build
npm start
```

## 🔍 Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Check running containers
docker ps

# View logs
docker logs price-data-api
docker logs price-data-scraper
```

### Log Files
- Application logs: `logs/app_YYYY-MM-DD.log`
- Error logs: `logs/error_YYYY-MM-DD.log`
- Scraping logs: `logs/scraping_YYYY-MM-DD.log`

## 🛡️ Data Model

### PriceData
```python
class PriceData(Base):
    id: int                    # Primary key
    prod_name: str            # Product name
    prod_catid: int           # Category ID
    prod_cat: str             # Category name
    low_price: float          # Minimum price
    high_price: float         # Maximum price
    avg_price: float          # Average price
    place: str                # Origin location
    unit_info: str            # Unit information
    pub_date: datetime        # Publication date
    created_at: datetime      # Record creation time
    updated_at: datetime      # Last update time
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `DATABASE_URL` | Database connection string | Required |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SCRAPE_INTERVAL` | Scraping interval (hours) | `3` |

### Docker Configuration

The project uses Docker Compose for orchestration:
- `api`: FastAPI application
- `scraper`: Data scraping service
- `db`: MySQL database
- `video-generator`: Next.js application (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write tests for new features
- Update documentation as needed
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

1. Check the [Issues](../../issues) page
2. Review the documentation
3. Check logs for error details
4. Create a new issue with detailed information

## 📈 Roadmap

- [ ] Real-time data streaming
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Multi-language support
- [ ] Advanced video templates
- [ ] Machine learning price predictions

---

**Note**: For Chinese documentation, see [README_zh.md](README_zh.md).
