CREATE SCHEMA IF NOT EXISTS weather_proj_lf;

CREATE TABLE IF NOT EXISTS city (
    city_id INT PRIMARY KEY,
    city_name VARCHAR(32),
    lat NUMERIC NOT NULL,
    long NUMERIC NOT NULL
)

CREATE TABLE IF NOT EXISTS observations (
    observation_id INT PRIMARY KEY,
    city_id INT NOT NULL,
    observation_date DATE NOT NULL,
    temp_2m_min NUMERIC(3,1),
    temp_2m_max NUMERIC(3,1),
    temp_2m_mean NUMERIC(3,1),
    precip_sum NUMERIC(5,1),
    precip_hours NUMERIC(3,1),
    windspeed_min NUMERIC(4,1),
    windspeed_max NUMERIC(4,1),
    windspeed_mean NUMERIC(4,1),
    CONSTRAINT city_id_fk FOREIGN KEY (city_id) REFERENCES weather_proj_lf.city(city_id)
)