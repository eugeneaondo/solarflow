-- Solar Panels Table
CREATE TABLE solar_panels (
    id SERIAL PRIMARY KEY,
    panel_id VARCHAR(50) UNIQUE NOT NULL,
    location VARCHAR(100),
    capacity_w DECIMAL(10, 2) DEFAULT 400.00,
    installation_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Solar Data Table (time-series)
CREATE TABLE solar_data (
    id BIGSERIAL PRIMARY KEY,
    panel_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    power_w DECIMAL(10, 2),
    voltage_v DECIMAL(5, 2),
    current_a DECIMAL(5, 2),
    temperature_c DECIMAL(5, 1),
    efficiency DECIMAL(5, 3),
    weather_factor DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (panel_id) REFERENCES solar_panels(panel_id)
);

-- Indexes for performance
CREATE INDEX idx_solar_data_panel_timestamp ON solar_data(panel_id, timestamp DESC);
CREATE INDEX idx_solar_data_timestamp ON solar_data(timestamp DESC);

-- Try sample panels
INSERT INTO solar_panels (panel_id, location, capacity_w) VALUES
('1', 'North Field A1', 400.00),
('2', 'North Field A2', 400.00),
('3', 'South Field B1', 400.00),
('4', 'South Field B2', 400.00),
('5', 'East Field C1', 400.00);

-- View for latest data
CREATE VIEW latest_panel_data AS
SELECT DISTINCT ON (panel_id)
    panel_id, timestamp, power_w, voltage_v, 
    current_a, temperature_c, efficiency
FROM solar_data
ORDER BY panel_id, timestamp DESC;