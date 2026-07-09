# weather analytics platform
## The cities chosen and the date range used
I picked three California cities, one from the north, central and southern California 
to compare and illustrate the vast climate differences California contains
North: Weed, CA
Central: San Francisco
South: Los Angeles

## Any data quality issues encountered
The data was very clean and generally easy to work with once I understood how the
parameterized api calls work.
When I started working on ingestion, I ran into some issues with truncated results.
Specifying lat/long for city locations was tedious.

## How those issues were resolved
I should have started with a shorter date range to understand the formatting better, though
once I had some time to explore the data, it was simple enough to use.

When I searched for lat/long locations for the cities I was working with, I found that open meteo 
has an api to search for cities by name, so I leveraged that to find the the three chosen cities 
by name and extract location data to return weather data wtih.