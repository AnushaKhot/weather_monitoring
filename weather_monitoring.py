import requests
import time
from datetime import datetime
import matplotlib.pyplot as plt

# OpenWeatherMap API key (replace with your own)
API_KEY = "3d8ecd9d6c99081fced65a35323959ed"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# List of cities to monitor
cities = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]

# Store daily summaries in this dictionary
daily_weather = {}

# Convert Kelvin to Celsius
def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

# Convert Kelvin to Fahrenheit
def kelvin_to_fahrenheit(kelvin):
    return (kelvin - 273.15) * 9/5 + 32

# Function to get weather data for a given city
def get_weather_data(city):
    params = {
        'q': city,
        'appid': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get data for {city}: {response.status_code}")
        return None

# Function to process weather data
def process_weather_data(city, weather_data):
    main_weather = weather_data['weather'][0]['main']
    temp_kelvin = weather_data['main']['temp']
    feels_like_kelvin = weather_data['main']['feels_like']
    temp_celsius = kelvin_to_celsius(temp_kelvin)
    feels_like_celsius = kelvin_to_celsius(feels_like_kelvin)
    timestamp = weather_data['dt']

    # Date of the data update (used for daily rollup)
    date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    # Initialize the daily summary if not already present
    if date not in daily_weather:
        daily_weather[date] = {
            'temps': [],
            'feels_like': [],
            'conditions': [],
            'max_temp': None,
            'min_temp': None
        }

    # Update daily summary
    daily_weather[date]['temps'].append(temp_celsius)
    daily_weather[date]['feels_like'].append(feels_like_celsius)
    daily_weather[date]['conditions'].append(main_weather)
    daily_weather[date]['max_temp'] = max(daily_weather[date]['temps'])
    daily_weather[date]['min_temp'] = min(daily_weather[date]['temps'])

# Function to calculate daily summary
def calculate_daily_summary(date):
    data = daily_weather.get(date)
    if not data:
        return None

    avg_temp = sum(data['temps']) / len(data['temps'])
    dominant_condition = max(set(data['conditions']), key=data['conditions'].count)
    max_temp = data['max_temp']
    min_temp = data['min_temp']

    return {
        'average_temp': avg_temp,
        'dominant_condition': dominant_condition,
        'max_temp': max_temp,
        'min_temp': min_temp
    }

# Define thresholds for alerts
ALERT_THRESHOLD = 35.0  # Celsius

# Function to check for threshold breaches
def check_for_alert(city, temp_celsius):
    if temp_celsius > ALERT_THRESHOLD:
        print(f"ALERT: {city} temperature exceeded {ALERT_THRESHOLD}°C: Current temp {temp_celsius}°C")

# Function to plot daily summaries
def plot_daily_summary(date):
    summary = calculate_daily_summary(date)
    if summary:
        temps = daily_weather[date]['temps']
        plt.plot(temps)
        plt.title(f"Temperature Trends for {date}")
        plt.xlabel('Time Intervals')
        plt.ylabel('Temperature (°C)')
        plt.show()
    else:
        print(f"No data available for {date}")

# Main program loop
def main():
    interval = 300  # 5 minutes

    while True:
        for city in cities:
            weather_data = get_weather_data(city)
            if weather_data:
                temp_celsius = kelvin_to_celsius(weather_data['main']['temp'])
                process_weather_data(city, weather_data)
                check_for_alert(city, temp_celsius)
        
        time.sleep(interval)  # Wait for 5 minutes before fetching data again

if __name__ == "__main__":
    main()
