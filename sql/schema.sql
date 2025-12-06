-- Multi-Source Data Ingestion Pipeline - Database Schema
-- Created: 2024-12-04

-- ============================================================================
-- STAGING TABLES (Raw Data)
-- ============================================================================

-- Staging: Weather API Data
CREATE TABLE IF NOT EXISTS stg_weather_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    country VARCHAR(10),
    temperature DECIMAL(5,2),
    feels_like DECIMAL(5,2),
    humidity INTEGER,
    pressure INTEGER,
    weather_condition VARCHAR(50),
    wind_speed DECIMAL(5,2),
    raw_data JSONB,
    extracted_at TIMESTAMP DEFAULT NOW(),
    load_id INTEGER
);

-- Staging: CSV File Data
CREATE TABLE IF NOT EXISTS stg_csv_data (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR(255),
    row_number INTEGER,
    raw_data JSONB,
    extracted_at TIMESTAMP DEFAULT NOW(),
    load_id INTEGER
);

-- Staging: Web Scraped Data
CREATE TABLE IF NOT EXISTS stg_scraped_data (
    id SERIAL PRIMARY KEY,
    source_url VARCHAR(500),
    title VARCHAR(500),
    content TEXT,
    scraped_date DATE,
    raw_html TEXT,
    extracted_at TIMESTAMP DEFAULT NOW(),
    load_id INTEGER
);

-- Staging: Source Database Data
CREATE TABLE IF NOT EXISTS stg_source_db_data (
    id SERIAL PRIMARY KEY,
    source_table VARCHAR(100),
    source_id INTEGER,
    raw_data JSONB,
    extracted_at TIMESTAMP DEFAULT NOW(),
    load_id INTEGER
);

-- ============================================================================
-- PRODUCTION TABLES (Validated/Transformed Data)
-- ============================================================================

-- Production: Weather Metrics
CREATE TABLE IF NOT EXISTS weather_metrics (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(10) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    feels_like DECIMAL(5,2),
    humidity INTEGER CHECK (humidity BETWEEN 0 AND 100),
    pressure INTEGER,
    weather_condition VARCHAR(50),
    wind_speed DECIMAL(5,2) CHECK (wind_speed >= 0),
    recorded_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(city, country, recorded_at)
);

-- Production: Business Data (from CSV)
CREATE TABLE IF NOT EXISTS business_data (
    id SERIAL PRIMARY KEY,
    business_date DATE NOT NULL,
    category VARCHAR(100),
    amount DECIMAL(12,2),
    description TEXT,
    metadata JSONB,
    loaded_at TIMESTAMP DEFAULT NOW()
);

-- Production: Web Content
CREATE TABLE IF NOT EXISTS web_content (
    id SERIAL PRIMARY KEY,
    source_url VARCHAR(500) NOT NULL,
    title VARCHAR(500),
    content TEXT,
    published_date DATE,
    scraped_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_url, published_date)
);

-- Production: Transactions (from source DB)
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    transaction_type VARCHAR(50),
    status VARCHAR(20),
    loaded_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- METADATA TABLES
-- ============================================================================

-- Pipeline Run Tracking
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'running', 'success', 'failed', 'partial'
    records_extracted INTEGER DEFAULT 0,
    records_validated INTEGER DEFAULT 0,
    records_loaded INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Data Quality Checks
CREATE TABLE IF NOT EXISTS data_quality_checks (
    check_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES pipeline_runs(run_id),
    source_type VARCHAR(50) NOT NULL,
    check_type VARCHAR(50) NOT NULL, -- 'null_check', 'type_check', 'range_check', etc.
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    status VARCHAR(20) NOT NULL, -- 'passed', 'failed', 'warning'
    records_checked INTEGER,
    records_passed INTEGER,
    records_failed INTEGER,
    check_details JSONB,
    checked_at TIMESTAMP DEFAULT NOW()
);

-- Error Log
CREATE TABLE IF NOT EXISTS error_log (
    error_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES pipeline_runs(run_id),
    source_type VARCHAR(50) NOT NULL,
    error_type VARCHAR(50), -- 'extraction_error', 'validation_error', 'loading_error'
    error_message TEXT NOT NULL,
    error_details JSONB,
    raw_data JSONB,
    retry_count INTEGER DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Staging indexes
CREATE INDEX IF NOT EXISTS idx_stg_weather_extracted_at ON stg_weather_data(extracted_at);
CREATE INDEX IF NOT EXISTS idx_stg_weather_load_id ON stg_weather_data(load_id);
CREATE INDEX IF NOT EXISTS idx_stg_csv_extracted_at ON stg_csv_data(extracted_at);
CREATE INDEX IF NOT EXISTS idx_stg_scraped_extracted_at ON stg_scraped_data(extracted_at);

-- Production indexes
CREATE INDEX IF NOT EXISTS idx_weather_city_country ON weather_metrics(city, country);
CREATE INDEX IF NOT EXISTS idx_weather_recorded_at ON weather_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_business_date ON business_data(business_date);
CREATE INDEX IF NOT EXISTS idx_web_content_scraped_at ON web_content(scraped_at);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);

-- Metadata indexes
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_source ON pipeline_runs(source_type);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_start_time ON pipeline_runs(start_time);
CREATE INDEX IF NOT EXISTS idx_dq_checks_run_id ON data_quality_checks(run_id);
CREATE INDEX IF NOT EXISTS idx_error_log_run_id ON error_log(run_id);
CREATE INDEX IF NOT EXISTS idx_error_log_created_at ON error_log(created_at);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Latest Weather Data
CREATE OR REPLACE VIEW v_latest_weather AS
SELECT DISTINCT ON (city, country)
    city,
    country,
    temperature,
    feels_like,
    humidity,
    weather_condition,
    wind_speed,
    recorded_at
FROM weather_metrics
ORDER BY city, country, recorded_at DESC;

-- View: Pipeline Performance Summary
CREATE OR REPLACE VIEW v_pipeline_summary AS
SELECT 
    pipeline_name,
    source_type,
    status,
    COUNT(*) as run_count,
    AVG(duration_seconds) as avg_duration_seconds,
    SUM(records_extracted) as total_records_extracted,
    SUM(records_loaded) as total_records_loaded,
    MAX(start_time) as last_run_time
FROM pipeline_runs
GROUP BY pipeline_name, source_type, status;

-- View: Recent Errors
CREATE OR REPLACE VIEW v_recent_errors AS
SELECT 
    e.error_id,
    p.pipeline_name,
    e.source_type,
    e.error_type,
    e.error_message,
    e.retry_count,
    e.resolved,
    e.created_at
FROM error_log e
LEFT JOIN pipeline_runs p ON e.run_id = p.run_id
WHERE e.created_at > NOW() - INTERVAL '7 days'
ORDER BY e.created_at DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Calculate pipeline duration when completed
CREATE OR REPLACE FUNCTION update_pipeline_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.end_time IS NOT NULL AND NEW.start_time IS NOT NULL THEN
        NEW.duration_seconds := EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-calculate duration
CREATE TRIGGER trg_update_pipeline_duration
    BEFORE UPDATE ON pipeline_runs
    FOR EACH ROW
    WHEN (NEW.end_time IS NOT NULL AND OLD.end_time IS NULL)
    EXECUTE FUNCTION update_pipeline_duration();

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert sample pipeline run
INSERT INTO pipeline_runs (
    pipeline_name, 
    source_type, 
    status, 
    start_time
) VALUES (
    'multi_source_ingestion',
    'initialization',
    'success',
    NOW()
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- PERMISSIONS (optional, for production)
-- ============================================================================

-- Grant permissions to dataeng user (if needed)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO dataeng;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dataeng;

-- ============================================================================
-- MAINTENANCE
-- ============================================================================

-- Clean up old staging data (run periodically)
-- DELETE FROM stg_weather_data WHERE extracted_at < NOW() - INTERVAL '30 days';
-- DELETE FROM stg_csv_data WHERE extracted_at < NOW() - INTERVAL '30 days';
-- DELETE FROM stg_scraped_data WHERE extracted_at < NOW() - INTERVAL '30 days';

COMMENT ON TABLE stg_weather_data IS 'Staging table for raw weather API data';
COMMENT ON TABLE weather_metrics IS 'Production table for validated weather metrics';
COMMENT ON TABLE pipeline_runs IS 'Tracks all pipeline execution runs';
COMMENT ON TABLE data_quality_checks IS 'Logs data quality validation results';
COMMENT ON TABLE error_log IS 'Stores errors and failed records for debugging';
