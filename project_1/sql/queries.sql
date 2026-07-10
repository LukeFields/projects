-- total precipitation per year by city
SELECT c.city_name, EXTRACT(YEAR FROM o.observation_date) observation_month, SUM(o.precip_sum) yearly_sum
FROM weather_proj_lf.observation o
JOIN weather_proj_lf.city c ON c.city_id = o.city_id
GROUP BY c.city_name, observation_month
ORDER BY yearly_sum DESC;

-- widest temperature gap
SELECT c.city_name, (MAX(o.temp_2m_max) - MIN(o.temp_2m_min)) diff, MAX(o.temp_2m_max) highest, MIN(o.temp_2m_min) lowest
FROM weather_proj_lf.observation o
JOIN weather_proj_lf.city c ON c.city_id = o.city_id
GROUP BY c.city_name
ORDER BY diff DESC;

-- calm days per year avg
WITH cte_years (yr)
AS (
	SELECT EXTRACT(YEAR FROM o.observation_date) yr
	FROM weather_proj_lf.observation o
	GROUP BY yr
)
SELECT c.city_name, (COUNT(o.windspeed_max) / (SELECT COUNT(*) FROM cte_years)) days_below_18kph
FROM weather_proj_lf.observation o
JOIN weather_proj_lf.city c ON c.city_id = o.city_id
WHERE windspeed_max < 18.0
GROUP BY c.city_name
ORDER BY days_below_18kph DESC;

-- average days of rain per month by city
WITH cte_years (yr)
AS (
	SELECT EXTRACT(YEAR FROM o.observation_date) yr
	FROM weather_proj_lf.observation o
	GROUP BY yr
)
SELECT 
	c.city_name, 
	EXTRACT(MONTH FROM o.observation_date) observation_month, 
	(COUNT(*) / (SELECT COUNT(*) FROM cte_years)) avg_days_of_rain
FROM weather_proj_lf.observation o
JOIN weather_proj_lf.city c ON c.city_id = o.city_id
WHERE o.precip_sum > 0.0
GROUP BY c.city_name, observation_month
ORDER BY city_name, avg_days_of_rain DESC;

-- yearly percentage of hours with precipitation
SELECT 
	c.city_name, 
	ROUND(SUM(o.precip_hours)  / COUNT(DISTINCT(EXTRACT(YEAR FROM o.observation_date)))) precip_hours_per_year, 
	ROUND((SUM(o.precip_hours) / (COUNT(o.observation_date) * 24)), 2) precipitation_time
FROM weather_proj_lf.observation o
JOIN weather_proj_lf.city c ON c.city_id = o.city_id
GROUP BY c.city_name
ORDER BY precipitation_time DESC;