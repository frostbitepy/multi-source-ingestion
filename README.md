# Project 1: Multi-Source Data Ingestion Pipeline

**Status**: In Progress  
**Start Date**: 2025-12-04  
**Estimated Completion**: 2-3 weeks

---

## Project Overview

A production-quality data ingestion system that extracts data from multiple sources (APIs, CSV files, web scraping, databases), validates the data, and loads it into PostgreSQL with proper error handling, logging, and monitoring.

### Objectives
- Demonstrate ability to work with multiple data sources
- Show production-ready code practices (error handling, logging, testing)
- Build modular, reusable components
- Create comprehensive documentation

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                             │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Weather API │   CSV Files  │ Web Scraping │ SQLite → PG    │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       └──────────────┴──────────────┴────────────────┘
                          │
                    ┌─────▼──────┐
                    │ Extractors │
                    └─────┬──────┘
                          │
                    ┌─────▼──────┐
                    │ Validators │
                    └─────┬──────┘
                          │
                    ┌─────▼──────┐
                    │   Loaders  │
                    └─────┬──────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐
    │  Staging │    │Production│    │ Metadata │
    │  Tables  │    │  Tables  │    │  Tables  │
    └──────────┘    └──────────┘    └──────────┘
                PostgreSQL Database
```

---

## Data Sources

### 1. Weather API
- **Source**: WeatherAPI (or similar free API)
- **Data**: Weather data for multiple cities
- **Frequency**: Daily
- **Format**: JSON

### 2. CSV Files
- **Source**: Local CSV files
- **Data**: Sample datasets (e.g., sales data, customer data)
- **Format**: CSV
- **Challenge**: Handle different delimiters, encodings

### 3. Web Scraping
- **Source**: Public website (e.g., news headlines, product listings)
- **Tool**: BeautifulSoup4
- **Format**: HTML → structured data
- **Challenge**: Handle pagination, rate limiting

### 4. Database-to-Database
- **Source**: SQLite database
- **Target**: PostgreSQL
- **Data**: Sample transactional data
- **Challenge**: Handle incremental loads

---

## Tech Stack

**Language**: Python 3.11+  
**Database**: PostgreSQL 15  
**Containerization**: Docker & Docker Compose  

**Python Libraries**:
- `requests` - API calls
- `pandas` - Data manipulation
- `psycopg2` or `SQLAlchemy` - PostgreSQL connection
- `BeautifulSoup4` - Web scraping
- `python-dotenv` - Environment variables
- `pytest` - Testing
- `pytest-cov` - Code coverage

---

## Project Structure

```
01-multi-source-ingestion/
├── README.md                 # This file
├── QUICKSTART.md            # Quick setup guide
├── docker-compose.yml       # Docker services
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
│
├── config/                 # Configuration files
│   ├── config.yaml         # Main configuration
│   └── logging_config.yaml # Logging configuration
│
├── src/                    # Source code
│   ├── __init__.py
│   ├── extractors/         # Data extractors
│   │   ├── __init__.py
│   │   ├── base_extractor.py
│   │   ├── api_extractor.py
│   │   ├── csv_extractor.py
│   │   ├── scraper_extractor.py
│   │   └── db_extractor.py
│   │
│   ├── validators/         # Data validators
│   │   ├── __init__.py
│   │   ├── base_validator.py
│   │   └── data_validator.py
│   │
│   ├── loaders/           # Data loaders
│   │   ├── __init__.py
│   │   ├── base_loader.py
│   │   └── postgres_loader.py
│   │
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── db_connection.py
│   │   └── helpers.py
│   │
│   └── main.py            # Main pipeline orchestration
│
├── sql/                   # SQL scripts
│   ├── schema.sql         # Database schema
│   ├── sample_queries.sql # Example queries
│   └── README.md          # SQL documentation
│
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── unit/              # Unit tests
│   │   ├── test_extractors.py
│   │   ├── test_validators.py
│   │   └── test_loaders.py
│   └── integration/       # Integration tests
│       └── test_pipeline.py
│
├── data/                  # Data directory (gitignored)
│   ├── raw/              # Raw extracted data
│   ├── processed/        # Processed data
│   └── archive/          # Archived data
│
├── logs/                  # Log files (gitignored)
│   └── pipeline.log
│
└── docs/                  # Additional documentation
    └── architecture.md    # Detailed architecture
```

---

## Database Schema

### Staging Tables (Raw Data)
- `stg_weather_data` - Raw weather API data
- `stg_csv_data` - Raw CSV data
- `stg_scraped_data` - Raw scraped data
- `stg_source_db_data` - Raw database transfer data

### Production Tables (Validated/Transformed)
- `weather_metrics` - Processed weather data
- `business_data` - Processed CSV data
- `web_content` - Processed scraped data
- `transactions` - Processed database data

### Metadata Tables
- `pipeline_runs` - Track pipeline executions
- `data_quality_checks` - Track validation results
- `error_log` - Track errors and failures

---

## Features

### Core Features
- [x] Modular extractor architecture
- [x] Multiple data source support (API, CSV, Web, DB)
- [ ] Data validation framework
- [ ] Error handling with retry logic
- [ ] Structured logging
- [ ] PostgreSQL staging and production tables
- [ ] Metadata tracking

### Nice-to-Have Features
- [ ] Incremental loading (only new/changed data)
- [ ] Data quality metrics dashboard
- [ ] Email/Slack notifications on failures
- [ ] Performance monitoring
- [ ] Dead letter queue for failed records

---

## Success Criteria

- [ ] All 4 extractors working reliably
- [ ] Data validation catches bad data
- [ ] Error handling tested (network failures, bad data)
- [ ] Unit test coverage >70%
- [ ] Integration tests passing
- [ ] Can run entire pipeline with: `docker-compose up`
- [ ] Documentation complete (README, QUICKSTART, docstrings)
- [ ] Can explain architecture in interview

---

## Learning Goals

### Technical Skills
- [x] Project structure and organization
- [ ] Modular Python design patterns
- [ ] Docker Compose multi-container setup
- [ ] Database schema design (staging, prod, metadata)
- [ ] Error handling and retry patterns
- [ ] Logging best practices
- [ ] Unit and integration testing
- [ ] Configuration management

### Soft Skills
- [ ] Documentation writing
- [ ] Code organization for maintainability
- [ ] Production-ready code standards

---

## Development Phases

### Phase 1: Setup (Week 1 - Days 1-2)
- [x] Project structure created
- [ ] Docker Compose configuration
- [ ] PostgreSQL setup with schema
- [ ] Basic logging framework
- [ ] Configuration management

### Phase 2: Extractors (Week 1 - Days 3-5)
- [ ] Weather API extractor
- [ ] CSV file extractor
- [ ] Web scraper extractor
- [ ] Database-to-database extractor

### Phase 3: Validation & Loading (Week 2 - Days 1-3)
- [ ] Data validation framework
- [ ] PostgreSQL loader
- [ ] Error handling and retries
- [ ] Metadata tracking

### Phase 4: Testing & Documentation (Week 2 - Days 4-7)
- [ ] Unit tests for all components
- [ ] Integration tests
- [ ] Documentation complete
- [ ] QUICKSTART guide tested

---

## Configuration

Configuration is managed through:
1. `.env` file - Sensitive credentials (API keys, DB passwords)
2. `config/config.yaml` - Application settings
3. Environment variables - Override defaults

**Example `.env`**:
```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=data_ingestion
POSTGRES_USER=dataeng
POSTGRES_PASSWORD=your_secure_password

# API Keys
WEATHER_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
```

---

## Monitoring & Logging

### Logging Strategy
- **INFO**: Pipeline start/end, major milestones
- **WARNING**: Recoverable issues (retry successful)
- **ERROR**: Failed operations (retry exhausted)
- **DEBUG**: Detailed execution info (development only)

### Metrics Tracked
- Records extracted per source
- Records validated (pass/fail)
- Records loaded to database
- Pipeline execution time
- Error rates by source

---

## Testing Strategy

### Unit Tests
- Test each extractor independently (mock API calls)
- Test validators with good/bad data
- Test loaders with mock database

### Integration Tests
- Test full pipeline end-to-end
- Test with Docker Compose
- Test error scenarios

### Test Data
- Sample CSV files
- Mock API responses
- Sample SQLite database

---

## Error Handling

### Retry Strategy
- **Transient errors** (network): Retry 3 times with exponential backoff
- **Permanent errors** (bad data): Log and move to error table
- **Critical errors** (DB down): Stop pipeline, alert

### Dead Letter Queue
Failed records are stored in `error_log` table for later review:
```sql
CREATE TABLE error_log (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50),
    error_message TEXT,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Next Steps

1. **Read QUICKSTART.md** - Get the project running
2. **Review SQL schema** - Understand database structure
3. **Start with API extractor** - Easiest to implement first
4. **Add tests as you go** - Don't wait until the end
5. **Keep documentation updated** - Document decisions and learnings

---

## Resources

### Documentation
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [pytest Documentation](https://docs.pytest.org/)

### APIs Used
- [OpenWeatherMap API](https://openweathermap.org/api) (free tier)
- Alternative: [WeatherAPI](https://www.weatherapi.com/) (free tier)

### Learning Resources
- [Real Python - SQL Databases](https://realpython.com/tutorials/databases/)
- [Docker for Data Science](https://www.docker.com/blog/)

---

## Contributing (For Portfolio Reviewers)

This is a portfolio project, but feedback is welcome! If you're reviewing this:

**What to look for**:
- Code quality and organization
- Error handling approach
- Testing coverage
- Documentation clarity

---

## License

This is a portfolio project - feel free to use as reference for your own learning.

---

**Last Updated**: 2025-12-04  
**Status**: Phase 1 - Setup in progress
