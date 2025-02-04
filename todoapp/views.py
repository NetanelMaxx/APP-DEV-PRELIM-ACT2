from django.shortcuts import render
import requests
from django.http import JsonResponse
import json
import urllib.request
from urllib.parse import quote
from urllib.error import HTTPError
from .models import Weather 

# Create your views here.
def home(request):
    weather_records = Weather.objects.all().order_by('-created_at')[:5]  # Fetch last 5 records

    if request.method == 'POST':
        city = request.POST['city']
        city_encoded = quote(city)

        try:
            # Make the API request
            print(f"Requesting weather data for: {city}")
            source = urllib.request.urlopen(
                'http://api.openweathermap.org/data/2.5/weather?q=' + city_encoded + '&units=metric&appid=58066e3f1e59826701042cf1016b9f73').read()
            print("API response:", source)                                                                          
            list_of_data = json.loads(source)

            # Debugging: Print the API response to the console
            print("API Response:", list_of_data)  # Print the API response

            # Check if the API returned valid data
            if list_of_data.get('cod') != 200:  # 200 means successful response
                print("Error in API response:", list_of_data)  # Print error data if not 200
                context = {
                    'error_message': 'City not found. Please try again.',
                    'weather_records': weather_records,
                }
                return render(request, "index.html", context)

            # Continue processing if data is valid...
            data = {
                "country_code": str(list_of_data['sys']['country']),
                "coordinates": str(list_of_data['coord']['lon']) + ', ' + str(list_of_data['coord']['lat']),
                "temperature": list_of_data['main']['temp'],
                "pressure": list_of_data['main']['pressure'],
                "humidity": list_of_data['main']['humidity'],
                'weather_main': str(list_of_data['weather'][0]['main']),
                'weather_description': str(list_of_data['weather'][0]['description']),
                'weather_icon': list_of_data['weather'][0]['icon'],
            }

            # Save to the database
            weather_record = Weather.objects.create(
                city=city,
                country_code=data['country_code'],
                coordinates=data['coordinates'],
                temperature=data['temperature'],
                pressure=data['pressure'],
                humidity=data['humidity'],
                weather_main=data['weather_main'],
                weather_description=data['weather_description'],
                weather_icon=data['weather_icon']
            )

            context = {
                'country_code': data['country_code'],
                'coordinate': data['coordinates'],
                'temp': data['temperature'],
                'pressure': data['pressure'],
                'humidity': data['humidity'],
                'main': data['weather_main'],
                'description': data['weather_description'],
                'icon': data['weather_icon'],
                'weather_record': weather_record,
                'weather_records': weather_records,
            }

        except HTTPError as e:
            # Handle HTTP error
            print("HTTP Error:", e)  # Print HTTP error
            context = {
                'error_message': 'City not found. Please try again.',
                'weather_records': weather_records,
            }

        except Exception as e:
            # Handle any other exception
            print("Exception:", e)  # Print general exception
            context = {
                'error_message': 'An error occurred. Please try again later.',
                'weather_records': weather_records,
            }

    else:
        context = {'weather_records': weather_records}

    return render(request, "index.html", context)
