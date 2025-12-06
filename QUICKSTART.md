# Quick Start Guide - Multi-Source Data Ingestion

**Get up and running in 10 minutes!**

---

## Prerequisites

- Docker Desktop installed and running
- Python 3.11+ installed
- Git (for cloning/committing)
- Text editor (VS Code recommended)

---

## 🚀 Quick Setup (10 minutes)

### Step 1: Navigate to Project Directory

```bash
cd projects/01-multi-source-ingestion
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
```

**Required variables in `.env`**:
```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=data_ingestion
POSTGRES_USER=dataeng
POSTGRES_PASSWORD=changeme123

# API Keys (get free key from openweathermap.org)
WEATHER_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
```

### Step 5: Start Docker Services

```bash
# Start PostgreSQL
docker-compose up -d

# Check it's running
docker-compose ps
```

### Step 6: Initialize Database

```bash
# Run schema creation
python -c "from src.utils.db_connection import init_database; init_database()"

# Or manually:
# docker exec -i postgres_db psql -U dataeng -d data_ingestion < sql/schema.sql
```

### Step 7: Run the Pipeline

```bash
# Run full pipeline
python src/main.py

# Or run specific extractor
python src/main.py --extractor api
```

---

## ✅ Verify It's Working

### Check Database

```bash
# Connect to PostgreSQL
docker exec -it postgres_db psql -U dataeng -d data_ingestion

# Check tables
\dt

# Query some data
SELECT COUNT(*) FROM stg_weather_data;
SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT 5;

# Exit
\q
```

### Check Logs

```bash
# View logs
tail -f logs/pipeline.log

# Or check specific date
cat logs/pipeline_2024-12-04.log
```

---

## 🧪 Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

View coverage report:
```bash
# Open coverage report in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## 🗂 Folder Structure Quick Reference

```
.
├── config/              # Configuration files
│   └── config.yaml     # Main config
│
├── src/                # Source code
│   ├── extractors/     # Data extraction
│   ├── validators/     # Data validation
│   ├── loaders/        # Data loading
│   ├── utils/          # Helper functions
│   └── main.py         # Entry point
│
├── sql/                # SQL scripts
│   └── schema.sql      # Database schema
│
├── tests/              # Tests
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
│
├── data/               # Data files (gitignored)
│   ├── raw/            # Raw data
│   └── processed/      # Processed data
│
└── logs/               # Log files (gitignored)
```

---

## 🔧 Common Commands

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f postgres

# Restart services
docker-compose restart

# Remove everything (including volumes)
docker-compose down -v
```

### Database Commands

```bash
# Access PostgreSQL CLI
docker exec -it postgres_db psql -U dataeng -d data_ingestion

# Run SQL file
docker exec -i postgres_db psql -U dataeng -d data_ingestion < sql/schema.sql

# Backup database
docker exec postgres_db pg_dump -U dataeng data_ingestion > backup.sql

# Restore database
docker exec -i postgres_db psql -U dataeng -d data_ingestion < backup.sql
```

### Python Commands

```bash
# Run main pipeline
python src/main.py

# Run with debug logging
LOG_LEVEL=DEBUG python src/main.py

# Run specific extractor
python src/extractors/api_extractor.py

# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

---

## 🐛 Troubleshooting

### Issue: Docker container won't start

**Solution**:
```bash
# Check if port 5432 is already in use
lsof -i :5432  # Mac/Linux
netstat -ano | findstr :5432  # Windows

# Stop conflicting service or change port in docker-compose.yml
```

### Issue: Can't connect to database

**Solution**:
```bash
# Check container is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Test connection
docker exec postgres_db pg_isready -U dataeng

# Restart services
docker-compose restart
```

### Issue: API extractor failing

**Solution**:
```bash
# Check API key is set
echo $WEATHER_API_KEY

# Test API manually
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"

# Check rate limits (free tier: 60 calls/min)
```

### Issue: Import errors

**Solution**:
```bash
# Make sure virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Tests failing

**Solution**:
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run tests with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_extractors.py::test_api_extractor -v
```

---

## 📊 Sample Queries to Try

```sql
-- Check pipeline runs
SELECT * FROM pipeline_runs 
ORDER BY created_at DESC 
LIMIT 10;

-- Check data quality
SELECT 
    source_type,
    COUNT(*) as total_records,
    SUM(CASE WHEN status = 'valid' THEN 1 ELSE 0 END) as valid_records,
    SUM(CASE WHEN status = 'invalid' THEN 1 ELSE 0 END) as invalid_records
FROM data_quality_checks
GROUP BY source_type;

-- Check recent weather data
SELECT * FROM weather_metrics 
ORDER BY recorded_at DESC 
LIMIT 10;

-- Check errors
SELECT * FROM error_log 
ORDER BY created_at DESC 
LIMIT 10;
```

---

## 🎯 Next Steps

Now that everything is running:

1. **Review the code** - Start with `src/main.py`
2. **Run extractors individually** - Understand each one
3. **Add your first test** - Pick a simple function
4. **Modify configuration** - Try different settings
5. **Add logging statements** - See what's happening
6. **Break something** - See how error handling works
7. **Read the main README** - Understand architecture

---

## 📚 Quick Reference Links

**Project Documentation**:
- [Main README](./README.md) - Full project documentation
- [SQL Scripts](./sql/README.md) - Database documentation
- [Architecture](./docs/architecture.md) - Detailed architecture

**External Docs**:
- [PostgreSQL Docs](https://www.postgresql.org/docs/15/index.html)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [pytest Documentation](https://docs.pytest.org/en/stable/)

---

## 💡 Tips for Development

1. **Keep Docker running** - Faster to restart than start/stop
2. **Use virtual environment** - Avoid dependency conflicts
3. **Check logs first** - Most issues show up in logs
4. **Write tests as you code** - Don't wait until the end
5. **Commit often** - Small commits are easier to review
6. **Use `.env` for secrets** - Never commit secrets to git

---

## 🆘 Still Stuck?

**Check these**:
- Docker Desktop is running
- Virtual environment is activated (`which python`)
- `.env` file exists and has correct values
- PostgreSQL container is healthy (`docker-compose ps`)
- No port conflicts (5432 for PostgreSQL)

**Get Help**:
- Check logs: `logs/pipeline.log`
- Check Docker logs: `docker-compose logs`
- Run with debug: `LOG_LEVEL=DEBUG python src/main.py`

---

**Ready to code!** 🚀

Open `src/main.py` and start exploring.
