# Standard imports
import datetime
import json
import math
import os
import time

# Third party imports
import dash
import requests
import plotly.graph_objects as go
import pytz
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
from timezonefinder import TimezoneFinder

# Initialize the Dash app
app = Dash(__name__, assets_folder='assets')
# Expose the underlying Flask server for deployment
server = app.server

# Define the app layout
app.layout = html.Div( # Main html.Div
    style={
        'display': 'flex',
        'flexDirection': 'column',
        'minHeight': '100vh', # Ensure full height
        'position': 'relative' # Make a positioning context
    }, # This section styles the whole app
    children=[ # Main child
        html.Div( # Second html.Div - Organize the main content area
            style={
                'flex': '1', # Take up the remaining vertical space
                'display': 'flex',
                'flexDirection': 'column', # Stack children vertically
                'alignItems': 'center', # Centre horizontally
                'justifyContent': 'flex-start', # Align to the top
                'width': '100%',
                'maxWidth': '1200px', # Limit the width
                'margin': '0 auto', # Centre the content
                'padding': '20px'
            },
            children=[ #Second child
                html.H1(
                    children='SkyLite',
                    style={
                        'textAlign': 'center',
                        'fontSize': '58px',
                        'marginBottom': '20px'
                    } # This section styles the heading
                ),
                html.Div( # Attribution for AccuWeather
                    id='aw-attribution',
                    style={
                        'position': 'absolute',
                        'top': '10px',
                        'right': '20px'
                    }
                ),
                html.Div( # Third html.Div
                    style={
                        'width': '95%',
                        'maxWidth': '900px',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'padding': '20px 0'
                    }, # This section styles the placement for the search input box
                    children=[ # Third child
                        html.Div( # Fourth html.Div
                            style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'width': '100%'
                            }, # This section styles the search button image of the search box
                            children=[ # Fourth child
                                dcc.Input(
                                    id='search-input',
                                    type='search',
                                    placeholder='Enter City, Country Code',
                                    style={
                                        'flex': '1', # Take up the available width
                                        'width': '100%', # Ensure full width
                                        'padding': '12px 20px', # Spacing the inside
                                        'margin': '8px 0', # Spacing the outide
                                        'display': 'inline-block',
                                        'border': '2px solid #000',
                                        'borderRadius': '16px', # Rounded corners
                                        'boxSizing': 'border-box', # Include padding in the width
                                        'fontSize': '18px',
                                        'lineHeight': '1.2' # Line spacing
                                    } # This section styles the search box
                                ),
                                html.Img(
                                    id='search-button-image',
                                    src='/assets/Image/SearchButtonImage.png',
                                    style={
                                        'width': '29px',
                                        'height': '29px',
                                        'cursor': 'pointer',
                                        'marginLeft': '10px',
                                        'marginTop': '5px',
                                        'marginBottom': '5px'
                                    } # This section styles the search button image of the search box
                                )
                            ] # Closing the fourth child
                        ) # Closing the fourth html.Div
                    ] # Closing the third child
                ), # Closing the third html.Div
                dcc.Dropdown(
                    id='source-select',
                    options=[
                        {'label': 'Open Weather', 'value': 'ow'},
                        {'label': 'Accu Weather', 'value': 'aw'}
                    ],
                    value='ow',
                    style={
                        'width': '50%',
                        'margin': '20px auto',
                        'placeholder': 'Please Choose a Weather Source'
                    } # This section styles the dropdown boxes for selecting the weather data source
                ),
                html.Div( # Fifth html.Div
                    id='search-output',
                    style={
                        'textAlign': 'center',
                        'marginTop': '20px',
                        'fontSize': '22px'
                    } # This section styles the output - which is controlled by the input in the search box
                ),
            ] # Closing the second child
        ), # Closing the second html.Div
        html.Footer(
            children=[ # Fifth child
                html.Div(
                    html.P(
                        html.A(
                            'Magnifying glass icons created by chehuna - Flaticon',
                            href='https://www.flaticon.com/free-icons/magnifying-glass',
                            target='_blank',
                            title='magnifying glass icons'
                        ),
                        style={
                            'fontSize': '12px',
                            'color': '#333333',
                        }
                    )
                ),
                html.Div( # Sixth html.Div - Attribution for OpenWeather
                    id='ow-attribution',
                    style={
                        'fontSize': '12px',
                        'color': '#333333',
                        'textAlign': 'center',
                        'marginTop': '5px',
                        'marginBottom': '5px'
                    },
                    children = []
                ),
                html.Div( # Seventh html.Div - To center the attribution button in the footer
                    style={
                        'width': 'auto',
                        'textAlign': 'center'
                    },
                    children=[
                        html.Button(
                            'Sources and Attribution Details for Images',
                            n_clicks=0,
                            id='attributions-button',
                            className='accordion-header',
                            style={
                                'cursor': 'pointer',
                                'textAlign': 'center',
                                'color': '#000000',
                                'width': 'auto',
                                'border': 'none',
                                'transition': 'background-color 0.3s ease'
                            } # This section styles the header text of the footer's image attribution's button
                        ),
                        html.Div( # For the attribution section
                            id='attributions-container',
                            className='accordion-container',
                            children=[
                                html.Div( # For the attribution text and links
                                    id='attributions-content',
                                    className='accordion-content',
                                    children = [],
                                    style={
                                        'textAlign': 'center',
                                        'display': 'none'
                                    }
                                ),
                            ],
                        ),
                        dcc.Store( # Store the visibility state of the attributions
                            id='attributions-visibility',
                            data={'is_visible': False}
                        ),
                    ],
                ), # Closing the seventh html.Div
            ], # Closing the fifth child
            style={
                'textAlign': 'center',
                'width': '100%',
                'backgroundColor': '#e0e0e0',
                'padding': 'auto',
                'flex-shrink': '0'
            } # This section styles the footer
        ) # Closing the footer
    ] # Closing the main child
) # Closing the main html.Div

# Initialize the API key for AccuWeather
API_AW_EF = None
# Initialize the API key for OpenWeather
API_OW_EF = None

# CATEGORY I - Fetching API and Formatting Time


def get_api_key():
    """
    Fetches the weather APIs from a JSON file.

    Args:
        None.

    Returns:
        True if the APIs were loaded successfully, False otherwise.
    """
    # Make the API avialble globally
    global API_AW_EF
    global API_OW_EF

    # Read API keys from environment variables
    API_AW_EF = os.getenv('ACCUWEATHER_API_KEY')
    API_OW_EF = os.getenv('OPENWEATHER_API_KEY')

    if API_AW_EF and API_OW_EF:
        print("API keys loaded successfully from environment variables.")
        return True
    else:
        print("Error: One or both API keys (ACCUWEATHER_API_KEY, OPENWEATHER_API_KEY) not found in environment variables.")
        return False
    
    # The following commented-out section was for local file-based API key loading and is disabled for secure public deployment.
    """
    filename = 'apiKeyWeatherForecast.json'
    # Create the full file path within the "assets" subdirectory
    filepath = os.path.join('assets', 'api_keys', filename)

    # Load the data
    try:
        with open(filepath, 'r') as f_api:
            api_data = json.load(f_api)

        # Assign them to their respective variables
        API_AW_EF = api_data.get('ACCUWEATHER_API_KEY', 'Not Available')
        API_OW_EF = api_data.get('OPENWEATHER_API_KEY', 'Not Available')

        # Return "True" if the APIs were loaded successfully without any errors
        return True

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print('An error occured while fetching the API keys!')
        print(f'Details: {e}\n\n')
        return False
    """

# Call the "get_api_key" function to get the APIs
get_api_key()

# API key for AccuWeather
API_AW = API_AW_EF
# API key for OpenWeather
API_OW = API_OW_EF


def format_time(time_str, output_format):
    """
    Formats a time string into a desired output format.

    Args:
        time_str (str): The input time string.
        output_format (str): The desired format string for the output time.

    Returns:
        str: The formatted time string, or 'Not Available' if the formatting fails.
    """
    # Check if "time_str" is empty
    if not time_str:
        return 'Not Available'
    
    try:
        # Check for the letter "T" in the "time_string"
        # Because AccuWeather's time stirngs use "T" as as separator between the date and the time, and OpenWeather's time strings use a space for this
        if 'T' in time_str: # AccuWeather format
            # AccuWeather's time srings use the letter "Z" at the end to indicate that the time is in UTC
            # Use "time_str.replace('Z', '+00:00')" to replace the "Z" (indicates UTC time) with "+00:00"
            # Which is equivalent to the UTC offset that the "fromisoformat" expects
            # UTC offset:
            #   It is the difference in hours and minutes between a particulat time zone and UTC. It tells how far ahead or behind a  local time is from UTC
            dt_obj = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            # Then use "dt_obj.strftime(output_format)" to format the 'datetime' object into the desired output format
            # "f' (UTC{dt_obj.strftime("%z")})'" - Creates a string that adds the UTC offset to the formatted time
            # The "%z" is a 'strftime' format code, which extracts the UTC offset form the 'datetime' obj (dt_obj) and formats it as either '+HHMM' or '-HHMM'
            return dt_obj.strftime(output_format) + f' (UTC{dt_obj.strftime("%z")})'
        
        else: # OpenWeather format
            # If "T" is not found, USE "datetime.datetime.strptime(...)" to parse the time string into a 'datetime' object
            dt_obj = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            # Then format this 'datetime' object using "dt_obj.strftime(output_format)"
            return dt_obj.strftime(output_format)
        
    except ValueError:
        print('Warning: Invalid date or time format: {time_str}')
        return 'Not Available'


# CATEGORY II - Data Fetching, Formatting, and Displaying AccuWeather Data


def get_location_key(search_text, max_retries=3, retry_delay=2):
    """
    Fetches location key for AccuWeather based on the search box input.

    Args:
        search_text (str): The "City, Country Code" to search for.
        max_retries (int): The maximum number of times to retry the API call in case of a failure. Defaults to three.
        retry_delay (int): The delay in seconds between retries. Defaults to two.

    Returns:
        str: The AccuWeather "location_key" or "None" if not found.
    """
    location_key_url = f'http://dataservice.accuweather.com/locations/v1/cities/search?q={search_text}&apikey={API_AW}'
    
    for attempt in range(max_retries):
        try:
            # Make a request to AccuWeather API using the 'location_key_url', and asks to find locations matching the '{search_text}'
            response = requests.get(location_key_url)
            # Check for HTTP status codes of the response.
            # If the status code indicates an error:
            #   It raises an exception
            #   And forces the code to jump to the 'except requests.exceptions.RequestException as Re' line
            response.raise_for_status()
            # If the API request was successful, it parses the JSON data in the response; and stores it in a variable 'locations'
            locations = response.json()
            # If everything went correctly, the function returns the 'location_key'
            return locations
    
        # Error handling for network errors, invalid URLs, etc.
        except requests.exceptions.RequestException as Re:
            print(f'Error fetching location!\nDetails: {Re}')
            if response is not None and response.status_code == 503:
                print(f'Received 503 error!\nRetrying in {retry_delay} seconds...')
                # The program pauses for the duration specified by the "retry_delay"
                time.sleep(retry_delay)
                # In the next step, the "retry_delay" is doubled to avoid overwhelming a temporarily overloaded server
                # Commonly known as exponential backoff
                retry_delay *= 2
            else:
                # If there was an error or no 'location_key' was found, the block returns 'None' to signal failure
                return None # Don't retry for other errors
    
        # Handle any other general errors
        except Exception as e:
            print(f'An unexpected error occured!\nDetails: {e}')
            # It also returns an empty list
            return None

    print(f'Max retries ({max_retries}) exceeded!\nUnable to fetch location key.')
    return None


def get_weather_forecast_aw(location_key, max_retries=3, retry_delay=2):
    """
    Fetches the 12-hour hourly forecast data for the given location key.

    Args:
        location_key (str): The AccuWeather location key.
        max_retries (int): The maximum number of times to retry the API call in case of a failure. Defaults to three.
        retry_delay (int): The delay in seconds between retries. Defaults to two.

    Returns:
        list or None: A list of dictionaries containing the 12-hour hourly forecast data, or None if an error occurs or no data is returned.
    """
    # Check if 'location_key' is empty or None, if it is the block return None, and prevents unnecessary API calls and potential errors
    if not location_key:
        return None
    
    forecast_url_aw = f'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}?apikey={API_AW}'
    
    for attempt in range(max_retries):
        try:
            response = requests.get(forecast_url_aw)
            response.raise_for_status()
            weather_data_aw = response.json()
            # If 'weather_data_aw' is not empty, the 'return'-block returns a list of dictionaries containing the 72-hour hourly forecast data
            # But if 'weather_data_aw' is empty, the 'return'-block returns None
            return weather_data_aw if weather_data_aw else None
    
        # Error handling for network errors, invalid URLs, etc.
        except requests.exceptions.RequestException as Re:
            print(f'Error fetching the weather data!\nDetails: {Re}')
            if response is not None and response.status_code == 503:
                print(f'Received 503 error!\nRetrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
                retry_delay *= 2 # Exponential backoff
            else:
                return None
    
        # Handle any other general errors
        except Exception as e:
            print(f'An unexpected error occured!\nDetails: {e}')
            return None

    print(f'Max retries ({max_retries}) exceeded!\nUnable to fetch weather data from AccuWeather.')
    return None


# Dictionary to associate weather descriptions with the corresponding image file paths - for AccuWeather
aw_icon_map = {
    '1': '/assets/AccuWeatherIcons/Sunny_(1).png',
    '2': '/assets/AccuWeatherIcons/MostlySunny_(2).png',
    '3': '/assets/AccuWeatherIcons/PartlySunny_(3).png',
    '4': '/assets/AccuWeatherIcons/IntermittentCloudsAtDay_(4).png',
    '5': '/assets/AccuWeatherIcons/HazySunshine_(5).png',
    '6': '/assets/AccuWeatherIcons/MostlyCloudyAtDay_(6).png',
    '7': '/assets/AccuWeatherIcons/Cloudy_(7).png',
    '8': '/assets/AccuWeatherIcons/Dreary(Overcast)_(8).png',
    '11': '/assets/AccuWeatherIcons/Fog_(11).png',
    '12': '/assets/AccuWeatherIcons/Showers_(12).png',
    '13': '/assets/AccuWeatherIcons/MostlyCloudyWithShowers_(13).png',
    '14': '/assets/AccuWeatherIcons/PartlySunnyWithShowers_(14).png',
    '15': '/assets/AccuWeatherIcons/ThunderStorms_(15).png',
    '16': '/assets/AccuWeatherIcons/MostlyCloudyWithThunderStorms_(16).png',
    '17': '/assets/AccuWeatherIcons/PartlySunnyWithThunderStorms_(17).png',
    '18': '/assets/AccuWeatherIcons/Rain_(18).png',
    '19': '/assets/AccuWeatherIcons/Flurries_(19).png',
    '20': '/assets/AccuWeatherIcons/MostlyCloudyWithFlurriesAtDay_(20).png',
    '21': '/assets/AccuWeatherIcons/PartlySunnyWithFlurries_(21).png',
    '22': '/assets/AccuWeatherIcons/Snow_(22).png',
    '23': '/assets/AccuWeatherIcons/MostlyCloudyWithSnowAtDay_(23).png',
    '24': '/assets/AccuWeatherIcons/Ice_(24).png',
    '25': '/assets/AccuWeatherIcons/Sleet_(25).png',
    '26': '/assets/AccuWeatherIcons/FreezingRain_(26).png',
    '29': '/assets/AccuWeatherIcons/RainAndSnow_(29).png',
    '30': '/assets/AccuWeatherIcons/Hot_(30).png',
    '31': '/assets/AccuWeatherIcons/Cold_(31).png',
    '32': '/assets/AccuWeatherIcons/Windy_(32).png',
    '33': '/assets/AccuWeatherIcons/Clear_(33).png',
    '34': '/assets/AccuWeatherIcons/MostlyClear_(34).png',
    '35': '/assets/AccuWeatherIcons/PartlyCloudy_(35).png',
    '36': '/assets/AccuWeatherIcons/IntermittentCloudsAtNight_(36).png',
    '37': '/assets/AccuWeatherIcons/HazyMoonlight_(37).png',
    '38': '/assets/AccuWeatherIcons/MostlyCloudyAtNight_(38).png',
    '39': '/assets/AccuWeatherIcons/PartlyCloudyWithShowers_(39).png',
    '40': '/assets/AccuWeatherIcons/MostlyCloudyWithShowers_(40).png',
    '41': '/assets/AccuWeatherIcons/PartlyCloudyWithThunderstorms_(41).png',
    '42': '/assets/AccuWeatherIcons/MostlyCloudyWithThunderstorms_(42).png',
    '43': '/assets/AccuWeatherIcons/MostlyCloudyWithFlurriesAtNight_(43).png',
    '44': '/assets/AccuWeatherIcons/MostlyCloudyWithSnowAtNight_(44).png',
    
}


def extract_aw_icon_id(hour_data):
    """
    Extarcts the weather path from AccuWeather data.

    Args:
        hour_data (dict): A dictionary containing the weather data for a single hour.

    Returns:
        str: The path to the appropriate icon, or a default path if not found or an error occurs.
    """
    try:
        # Safely access the value associated with the key 'WeatherIcon' from the "hour_data" dictionary
        icon_id = hour_data.get('WeatherIcon', None)
        
        # Check if "icon_id" exists
        if icon_id is not None:
            # Convert the extracted "icon_id" to a string
            # Then try to find the corresponding icon path in the "aw_icon_map" dictionary, using the string version of "icon_id" as the key
            # If "icon_id" is not found in the dictionary, the "icon_path" is set to the default icon path
            icon_path = aw_icon_map.get(str(icon_id), '/assets/AccuWeatherIcons/DefaultImageAW.png')

            # Return the determined "icon_path"
            return icon_path

        # Handle missing 'WeatherIcon' key
        else:
            icon_path = '/assets/AccuWeatherIcons/DefaultImageAW.png'
            return icon_path
        
    except (KeyError, TypeError) as e:
        print(f"Encountered an error extracting AccuWeather's weather icon.\nDetails: {e}")
        icon_path = '/assets/AccuWeatherIcons/DefaultImageAW.png'
        # Return the default "icon_path"
        return icon_path


def create_aw_weather_card(hour_data):
    """
    Creates a Dash html Div for a single hour's AccuWeather data.

    Args:
        hour_data (dict): A dictionary containg the weather data for a single hour.

    Returns:
        html.Div: A Dash html Div component.
    """
    # Extract the raw time string from "hour_data", which is associated with the key "DateTime"
    time_str = hour_data.get('DateTime', None)
    # Call the "format_time" function to format the raw time string
    # "%B" - Full name of the month
    # "%I" - Hour (12-hour clock) as a zero padded number
    # "%p" - AM or PM
    formatted_time_aw = format_time(time_str, '%B %d, %Y, %I:%M %p')

    # Call the "extract_aw_icon_id" function to determine the file path of the appropriate weather icon based on the "hour_data"
    icon_path = extract_aw_icon_id(hour_data)
            
    # Create the html.Div to represent the AccuWeather weather card
    return html.Div(
        style={
            'border': '1px solid #e0e0e0',
            'borderRadius': '10px',
            'boxShadow': '2px 2px 8px rgba(0, 0, 0, 0.1)',
            'padding': '15px',
            'margin': '10px',
            'flexBasis': 'calc(33% - 20px)',
            'boxSizing': 'border-box',
            'display': 'inline-block',
            'fontFamily': 'Arial, sans-serif',
            'backgroundColor': '#f0f0f0'
        }, # Styles the appearance of the card
        children=[
            html.H3(
                f'Time: {formatted_time_aw}',
                style={
                    'fontSize': '16px',
                    'fontWeight': 'bold',
                    'marginBottom': '10px',
                    'color': '2c3e50'
                }
                ),
                html.Img(
                    src=icon_path,
                    style={
                        'height': '80px',
                        'width': '80px'
                    }
                ),
                html.Div( # Group temperature-realted information - arranging verically
                    style={
                        'display': 'flex', # Using a flexbox
                        'flexDirection': 'column', # Stacking the items vertically
                        'marginBottom': '8px' # Adding some space below
                    },
                    children=[
                        html.P(
                            f'Temperature: {hour_data.get("Temperature", {}).get("Value", "Not Available")}°{hour_data.get("Temperature", {}).get("Unit", "N/A")}',
                            style={
                                'fontSize': '21px',
                                'fontFamily': 'Franklin Gothic Heavy'
                            }
                        )
                    ]
                ),
                html.P(f'Conditions: {hour_data.get("IconPhrase", "Not Available").title()}',
                    style={
                        'fontSize': '18px',
                        'lineHeight': '1.4',
                        'fontFamily': 'Footlight MT Light'
                    }
                ),
                html.P(
                    f'Precipitation: {"Yes" if hour_data.get("HasPrecipitation", False) else "No"}',
                    style={
                        'fontSize': '18px',
                        'fontFamily': 'Gill Sans MT'
                    }
                ),
                html.P(
                    f'Precipitation Probability: {hour_data.get("PrecipitationProbability", "Not Available")}%',
                    style={
                        'fontSize': '18px',
                        'fontFamily': 'Perpetua'
                    }
                ),
                html.P(
                    f'Day Light: {"Yes" if hour_data.get("IsDaylight", False) else "No"}',
                    style={
                        'fontSize': '18px',
                        'fontFamily': 'Constantia'
                    }
                ),
            ]
        )


def extract_aw_plotting_data(forecast_data):
    """
    Extracts time and temperature data from AccuWeather forecast data for plotting.

    Args:
        forecast_data (list): A list of hourly forecast data from AccuWeather.

    Returns:
        dict: A dictionary containing lists of time and corresponding temperatures.
    """
    # Create two empty lists to store the extracted time strings and the corresponding temperature values
    times = []
    temps = []

    # Ensure forecast_data is not empty or None
    if forecast_data:
        
        # Iterate through each "hour_data" in the "forecast_data" list
        for hour_data in forecast_data:
            
            # Extract the time string
            time_str = hour_data.get('DateTime')
            
            # Check that "time_str" is valid
            if time_str:
                # Format the time for display (without the time zone)
                formatted_time = format_time(time_str, '%Y-%m-%d %H:%M:%S')
                # Append the formatted time into the empty "times" list
                times.append(formatted_time)

                # Extract the temperature (from "hour_data")
                # Get the dictionary associated with the key "Temperature"; if "Temperature" is not found it defaults to an empty dictionary - to avoid errors
                # If successful, get the value associated with the key "Value" from this dictionary. If not found, it returns "None" by default
                # Append the extracted temperature to the empty "temps" list
                temps.append(hour_data.get('Temperature', {}).get('Value'))
                
    return {'times': times, 'temps': temps}


def create_aw_temperature_graph(plotting_data):
    """
    Creates a Dash graph component to show AccuWeather temperature data against time.

    Args:
        plotting_data (dict): A dictionary containing "times" and "temps".

    Returns:
        dcc.Graph: A Dash graph component displaying the temperature over time.
    """
    if plotting_data and plotting_data['times'] and plotting_data['temps']:
        # Create the graph
        fig = go.Figure(
            # The "data" argument is a list containing the data to be plotted
            data=[
                go.Scatter(
                    # Extract the data
                    x=plotting_data['times'],
                    y=plotting_data['temps'],
                    mode='lines+markers', # The graph should display both, lines connecting the data points and markers at the data points themselves
                    line=dict(color='#2e38f3', width=2),
                    marker=dict(color='#fc0349', size=6)
                )
            ],
            # Design the layout
            layout=go.Layout(
                title='Temperature Over Time',
                xaxis_title='Time',
                yaxis_title='Temperature (°F)',
                template='plotly_white',
                xaxis=dict(showgrid=True, gridcolor='lightgray'),
                yaxis=dict(showgrid=True, gridcolor='lightgray'),
            ),
        )
        # The "figure=fig" argument passes the plotly figure created in the previous step to the "dcc.Graph" component
        # The "dcc.Graph" is then returned, making the interactive graph avaialable to be displayed in the Dash app's user interface
        return dcc.Graph(figure=fig)
    
    else:
        return html.P('No temperature data available for graph!')


def aw_data_processing(search_text):
    """
    Fetches and processes the weather data from AccuWeather.

    Args:
        search_text (str): The text entered in the search input box.

    Returns:
        list: A list of Dash HTML components to display the AccuWeather data.
    """
    # Fetch the "location_key" by calling "get_location_key" function to obtain the location key from AccuWeather based on the user's "search_text"
    locations_aw = get_location_key(search_text)
    if locations_aw:
        # If "location_key" is found - "locations_aw[0]['Key']" extracts the first location's key
        location_key = locations_aw[0]['Key']
        # Call the "get_weather_forecast_aw" function to get the 12-hour hourly forecast data from AccuWeather
        forecast_aw = get_weather_forecast_aw(location_key)
    else:
        # If "get_location_key" fails, it sets "forecast_aw" to None
        forecast_aw = None

    # Initialize a Children list
    # This list will store:
    #   Dash HTML components that will be displayed in the app
    #   These components will include weather cards and a temperature graph
    children = []
    
    # Process and prepare the data for display
    if forecast_aw:
        # Limit the number of entries to the first 12
        forecast_aw = forecast_aw[:12]
                
        # Create an empty list to store the weather cards
        weather_cards_aw = []

        # Iterate through each hour's data in the "forecast_aw"
        for hour_data in forecast_aw:
            # For each hour, call the "create_aw_weather_card" to create a Dash 'html.Div' element (a weather card)
            # That displays the weather information for that particular hour
            # Then the generated weather card is appended to "weather_cards_aw" list
            weather_cards_aw.append(create_aw_weather_card(hour_data))

        # After processing all the hourly data, it creates a 'html.Div' to contain all the weather cards
        # This 'html.Div' uses flexbox to arrange the cards horizontally and wrap them if they exceed the container's width
        children.append(
            html.Div(
                style={
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'justifyContent': 'flex-start'
                },
                children = weather_cards_aw[:12] # Adds the list of weather cards as children
            )
        )
        # Create and append the temperaure graph

        # Call the "extract_aw_plotting_data" to prepare the forecast data for creating a temperature graph
        plotting_data_aw = extract_aw_plotting_data(forecast_aw)
        # Call the "create_aw_temperature_graph" to generate a Dash 'dcc.Graph' component that displays the temperature over time
        temp_graph_aw = create_aw_temperature_graph(plotting_data_aw)

        # Append the temperature graph to the "children" list
        children.append(temp_graph_aw)

        # Finally, if the forecast data was successfully processed, the return the "children" list
        # Which now contains the weather cards and the temperature graph
        return children

    # Handle if 'forecast_aw" is None
    return [html.P('Sorry, could not retrieve weather data from AccuWeather!')]


# CATEGORY III - Data Fetching, Formatting, and Displaying OpenWeather Data


def get_coordinates(city_name, api_key=API_OW, max_retries=3, retry_delay=2):
    """
    Fetches the latitude and longitude of a city.

    Args:
        city_name (str): The name of the city.
        api_key: OpenWeather API key.
        max_retries (int): The maximum number of times to retry the API call in case of a failure. Defaults to three.
        retry_delay (int): The delay in seconds between retries. Defaults to two.

    Returns:
        tuple or None: A tuple containing 'latitude, longitude' if found, otherwise None.
        Returns the first result if multiple are found.
    """
    geocoding_url = 'http://api.openweathermap.org/geo/1.0/direct'
    # This is a dictionary, which will be used as query parameters in the API request
    params = {
        'q': city_name,
        'limit': 1, # Tell the API to return at most one result
        'appid': api_key
    }
    latitude = None
    longitude = None
    for attempt in range(max_retries):
        try:
            response = requests.get(geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data:
                # If "data" is found, "data[0]" takes the first element of the list - which is a dictionary containing information about the location
                # It then extracts the values associated with the keys "lat" and "lon", and returns them as a tuple
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                return latitude, longitude
            else: # If the "data" list is empty
                print(f'Sorry, could not find latitude and longitude for {city_name}!')
                return None

        # Error handling for network errors, invalid URLs, etc.   
        except requests.exceptions.RequestException as Re:
            print(f'Error fetching the latitude and longitude!\nDetails: {Re}')
            if response is not None and response.status_code == 503:
                print(f'Received 503 error!\nRetrying in {retry_delay} seconds...')
                # The program pauses for the duration specified by the "retry_delay"
                time.sleep(retry_delay)
                # In the next step, the "retry_delay" is doubled to avoid overwhelming a temporarily overloaded server
                # Commonly known as exponential backoff
                retry_delay *= 2
            else:
                return None
    
        # Handle any other general errors
        except Exception as e:
            print(f'An unexpected error occured!\nDetails: {e}')
            return None

    print(f'Max retries ({max_retries}) exceeded!\nUnable to fetch latitude and logitude.')
    return None


def get_weather_forecast_ow(latitude, longitude, api_key=API_OW, exclude='minutely,hourly,alerts', units='imperial', max_retries=3, retry_delay=2):
    """
    Fetches the forecast data for the given latitude and longitude.

    Args:
        latitude (float): The latitude of the location.
        longitude (float):  The longitude of the location.
        api_key: OpenWeather API key.
        exclude: Parts of foercast to exclude.
        units (str): The unit system to use for the forecast.
                     Possible values: 'standard' (Kelvin), 'metric' (Celsius), and 'imperial' (Fahrenheit).
                     Defaults to "imperial".
        max_retries (int): The maximum number of times to retry the API call in case of a failure. Defaults to three.
        retry_delay (int): The delay in seconds between retries. Defaults to two.

    Returns:
        dict or None: If successful, returns the weather data in a JSON format, otherwise returns None.
    """
    forecast_url_ow = 'https://api.openweathermap.org/data/2.5/forecast'
    params = {
        'lat': latitude,
        'lon': longitude,
        'exclude': exclude,
        'appid': api_key,
        'units': units
    }
    for attempt in range(max_retries):
        try:
            response = requests.get(forecast_url_ow, params=params)
            response.raise_for_status()
            forecast_data_ow = response.json()
            
            return forecast_data_ow

        # Error handling for network errors, invalid URLs, etc.
        except requests.exceptions.RequestException as Re:
            print(f'Error fetching the weather data from OpenWeather!\nDetails: {Re}')
            if response is not None and response.status_code == 503:
                print(f'Received 503 error!\nRetrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
                retry_delay *= 2 # Exponential backoff
            else:
                return None

        # Handle any other general errors
        except Exception as e:
            print(f'An unexpected error occured!\nDetails: {e}')
            return None

    print(f'Max retries ({max_retries}) exceeded!\nUnable to fetch weather data from OpenWeather.')
    return None


def dew_point(forecast_data_ow):
    """
    Calculate dew point from humidity as obtained by OpenWeather.

    Args:
        forecast_data_ow (dict): A dictionary containing the weather forecast data from OpenWeather.

    Returns:
        float or None: The calculated dew point in Fahrenheit, or None if encounters an error.
    """
    # Initialize the temperature_celsius
    temperature_celsius = None
    
    # Fetch the humidity data
    humidity = forecast_data_ow.get('humidity')
    
    # Fetch the temperature data
    temperature_fahrenheit = forecast_data_ow.get('temp')

    if temperature_fahrenheit is None or humidity is None:
        return None

    # Convert Fahrenheit to Celsius
    temperature_celsius = (temperature_fahrenheit - 32) * 5 / 9

    # Covert humidity to relative humidity
    relative_humidity = humidity / 100

    # Set the constants
    a = 17.27
    b = 237.7

    # Calculate the dew point
    try:
        numerator = (b * math.log(relative_humidity / 100) + a * temperature_celsius)
        denominator = (a - math.log(relative_humidity / 100) - a * temperature_celsius / (b + temperature_celsius))
        dew_point_celsius = numerator / denominator
        return dew_point_celsius * 9 / 5 + 32
        
    # Handle potential math errors
    except (ValueError, ZeroDivisionError) as e:
        print(f'Encountered an error!\nDetails: {e}')
        return None


def get_wind_speed(forecast):
    """
    Extracts the wind speed from the forecast data.

    Args:
        forecast (dict): A dictionary containing the forecast data.

    Returns:
        str or 'Not Available': The wind speed or 'Not Available' if not found.
    """
    # First check if "wind" exists directly in the "forecast" dictionary
    if 'wind' in forecast:
        # If it does, use ".get(...)" to retrieve the value associated with the key "speed" within the "wind" sub-dictionary
        # If the "speed" key is found, it returns its value (wind speed)
        # Otherwise, it returns a default value - "Not Available"
        return forecast['wind'].get('speed', 'Not Available')

    # If the "wind" key is not found directly, check if the "weather" key exists in the "forecast" dictionary
    # "len(forecast['weather']) > 0" - check that the "weather" list has at least one element
    # Now check if "wind" exists within the first element of the "weather" list (forecast['weather'][0])
    elif 'weather' in forecast and len(forecast['weather']) > 0 and 'wind' in forecast['weather'][0]:
        # If found, retrieve the wind speed using ".get(...)", otherwise return the default value - "Not Available"
        return forecast['wind'][0].get('speed', 'Not Available')

    # If nothing is found, return "Not Available"
    else:
        return 'Not Available'


def get_visibility(forecast):
    """
    Extracts the visibility from the forecast data.

    Args:
        forecast (dict): A dictionary containing the forecast data.

    Returns:
        str or 'Not Available': The visibility or 'Not Available' if not found.
    """
    if 'visibility' in forecast:
        return forecast['visibility']
    
    elif 'weather' in forecast and len(forecast['weather']) > 0 and 'visibility' in forecast['weather'][0]:
        return forecast['weather'][0].get('visibility', 'Not Available')
    
    else:
        return 'Not Available'


def extract_ow_sunrise_sunset_location(forecast_ow):
    """
    Extracts the sunrise time, sunset time, and location (latitude, longitude) from OpenWeather for correct weather icon selection.

    Args:
        forecast_ow (dict): A dictionary containing the forecast data from openWeather.

    Returns:
        A tuple containg:
            str: Formatted sunrise time, or None if not found.
            str: Formatted sunset time, or None if not found.
            float: Latitude, or None if not found.
            float: Longitude, or None if not found.
    """
    # Initialize the variables
    formatted_sunrise = None
    formatted_sunset = None
    latitude = None
    longitude = None
    
    if forecast_ow and 'city' in forecast_ow:
        city_data = forecast_ow.get('city', {})
        sunrise_timestamp = city_data.get('sunrise', None)
        sunset_timestamp = city_data.get('sunset', None)
        coord_data = city_data.get('coord', {})

        if coord_data:
            latitude = coord_data.get('lat', None)
            longitude = coord_data.get('lon', None)

            # 1. Finding the timezone
            # Create an instance of the "TimezoneFinder" class
            tf = TimezoneFinder()
            # Call the "timezone_at()" method of the "TimezoneFinder" object
            # It returns a string representing the timezone name (e.g., America/New_York)
            # If no timezone is found for the given coordinates, it will return "None"
            timezone_str = tf.timezone_at(lng=longitude, lat=latitude)

            # 2. Using the timezone
            # Check if the timezone string is retrieved successfully
            if timezone_str:
                # "local_tz = pytz.timezone(...)" - If a timezone string is found, use the "pytz" library to create a timezone object based on the retrieved string
                # "local_tz" object represents the specific timezone of the location
                local_tz = pytz.timezone(timezone_str)

                # 3. Processing sunrise time
                # Check if a "sunrise_timestamp" was obtained from the OpenWeather data
                if sunrise_timestamp is not None:
                    try:
                        # "datetime.datetime.fromtimestamp(sunrise_timestamp)" - Convert the Unix timestamp into a "datetime" object
                        # "tz=pytz.utc" - Explicitly tell Python that the initial "datetime" object represents a time in UTC (Coordinated Universal Time)
                        utc_sunrise_time = datetime.datetime.fromtimestamp(sunrise_timestamp, tz=pytz.utc)
                        # Timezone conversion:
                        #   The ".astimezone(local_tz)" method takes the UTC "datetime" object
                        #   Converts it to the time in the "local_tz" which has been determined earlier using "TimezoneFinder"
                        local_sunrise_time = utc_sunrise_time.astimezone(local_tz)
                        # Format the local sunrise time into a string with the format "HH:MM AM/PM"
                        formatted_sunrise = local_sunrise_time.strftime('%I:%M %p')
                        
                    except (TypeError, ValueError) as e:
                        print(f'An error occured while processing "sunrise_time".\nDetails: {e}')

                # 4. Processing sunrise time
                if sunset_timestamp is not None:
                    try:
                        utc_sunset_time = datetime.datetime.fromtimestamp(sunset_timestamp, tz=pytz.utc)
                        local_sunset_time = utc_sunset_time.astimezone(local_tz)
                        formatted_sunset = local_sunset_time.strftime('%I:%M %p')
                    except (TypeError, ValueError) as e:
                        print(f'n error occured while processing "sunset_time".\nDetails: {e}')
            else:
                print('Could not determine timezone from coordinates.')
        else:
            print('Coordinates data (latitude and longitude) not found.')
    else:
        print('"city_data" not found in "forecast_ow"!')

    return formatted_sunrise, formatted_sunset, latitude, longitude


def override_ow_icon_code(forecast, icon_code, forecast_ow):
    """
    Override the original icon code provided by OpenWeather if it is incorrect.

    Args:
        forecast (dict): A dictionary containg the forecast data for a single time. 
        icon_code (str): The original OpenWeather icon code.
        forecast_ow (dict): The entire forecast data from OpenWeather, containing the sunrise and the sunset timestamps.

    Returns:
        str: The overriddden icon path, or the original icon path if no override is required.
    """
    # Fetch the forecast time from the "forecast" dictionary using the key 'dt_txt'. If not found, default to "Not Avaialble"
    time_str = forecast.get('dt_txt', 'Not Avaialble')
    if not time_str:
        print('Time string is not available. Cannot override icon codes!')
        # If "time_str" is not available, return the original icon code
        return icon_code

    try:
        # Covert the "time_str" into a "datetime" object
        # "current_time" represents the time for which the forecast is being considered
        current_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

        # Call the "extract_ow_sunrise_sunset_location" function with the complete "forecast_ow" data
        # The "extract_ow_sunrise_sunset_location" function returns formatted sunrise and sunset time, latitude, and longitude
        # And because only the sunrise and sunset time are required, only unpack the tuple and ignore the latitude and longitude using "_"
        sunrise_time, sunset_time, _, _ = extract_ow_sunrise_sunset_location(forecast_ow)

        if sunrise_time and sunset_time:
            # "datetime.datetime.strptime(sunrise_time, '%I:%M %p').time()" - Parse the formatted sunrise time string into a "date.time" object
            sunrise = datetime.datetime.strptime(sunrise_time, '%I:%M %p').time()
            sunset = datetime.datetime.strptime(sunset_time, '%I:%M %p').time()
            # "datetime.datetime.combine(current_time.date(), sunrise)" - Combine the date of the current forecast ("current_time.date()") with the time of sunrise
            # To create a full "datetime" object for the sunrise on that day
            sunrise_datetime = datetime.datetime.combine(current_time.date(), sunrise)
            sunset_datetime = datetime.datetime.combine(current_time.date(), sunset)
            
            # Compare the "current_time" with sunrise and sunset
            # Check if the "current_time" of the forecast fall between the "sunrise_datetime" and "sunset_datetime" on the same day. If it does, it means it is daytime
            if sunrise_datetime <= current_time <= sunset_datetime:
                # If it is daytime, and the "icon_code" ends with "n" (which indicates night), replace the "n" with "d", effectively overriding the icon to a day icon
                if icon_code.endswith('n'):
                    icon_code = icon_code.replace('n', 'd')
            else:
                if icon_code.endswith('d'):
                    icon_code = icon_code.replace('d', 'n')

    except ValueError as e:
        print(f'An error occured while comparing sunrise or sunset!\nDetails: {e}')
    except Exception as e:
        print(f'An unexpected error occured in the "override_ow_icon_code" function!\nDetails: {e}\n'
                f'sunrise time: {sunrise_time}, sunset time: {sunset_time}, time_str: {time_str}')

    # Return the potentially overridden "icon_code"        
    return icon_code


# Dictionary to associate weather descriptions with the corresponding image file paths - for OpenWeather
ow_icon_map = {
    '01d': '/assets/OpenWeatherIcons/ClearSkyDay_(01d).png',
    '01n': '/assets/OpenWeatherIcons/ClearSkyNight_(01n).png',
    '02d': '/assets/OpenWeatherIcons/FewCloudsDay_(02d).png',
    '02n': '/assets/OpenWeatherIcons/FewCloudsNight_(02n).png',
    '03d': '/assets/OpenWeatherIcons/ScatteredCloudsDay_(03d).png',
    '03n': '/assets/OpenWeatherIcons/ScatteredCloudsNight_(03n).png',
    '04d': '/assets/OpenWeatherIcons/BrokenCloudsDay_(04d).png',
    '04n': '/assets/OpenWeatherIcons/BrokenCloudsNight_(04n).png',
    '09d': '/assets/OpenWeatherIcons/ShowerRainDay_(09d).png',
    '09n': '/assets/OpenWeatherIcons/ShowerRainNight_(09n).png',
    '10d': '/assets/OpenWeatherIcons/RainDay_(10d).png',
    '10n': '/assets/OpenWeatherIcons/RainNight_(10n).png',
    '11d': '/assets/OpenWeatherIcons/ThunderstormDay_(11d).png',
    '11n': '/assets/OpenWeatherIcons/ThunderstormNight_(11n).png',
    '13d': '/assets/OpenWeatherIcons/SnowDay_(13d).png',
    '13n': '/assets/OpenWeatherIcons/SnowNight_(13n).png',
    '50d': '/assets/OpenWeatherIcons/MistDay_(50d).png',
    '50n': '/assets/OpenWeatherIcons/MistNight_(50n).png',
}


def extract_ow_icon_code(forecast, forecast_ow):
    """
    Extarcts the icon code path from a single weather forecast entry, from OpenWeather data.

    Args:
        forecast (dist): A dictionary containing the weather data for a single time.
        forecast_ow (dict): The entire forecast data from OpenWeather.

    Returns:
        str: The path to the appropriate icon, or a default path if not found or an error occurs.
    """
    # Extract the initial icon code
    # "forecast.get('weather', [{}])" - Get the value associated with the key 'weather'. If not found, default to a list containing an empty dictionary "[{}]"
    # "[0]" - Extract the first element of the list (the value associated with the key 'weather' is a list)
    # ".get('icon')" - Get the value associated with the key 'icon'. If not found, default to "None"
    icon_code = forecast.get('weather', [{}])[0].get('icon')

    # Call the "override_ow_icon_code" function to correct the potential inaccuracies in the icon codes
    overridden_icon_code = override_ow_icon_code(forecast, icon_code, forecast_ow)

    # Check if the "overridden_icon_code" exists as a key in the "ow_icon_map" dictionary
    if overridden_icon_code in ow_icon_map:
        # Map the potentially overridden icon code to a path
        icon_path = ow_icon_map.get(overridden_icon_code, '/assets/OpenWeatherIcons/DefaultImageOW.png')
    else:
        # Return the default "icon_path"
        icon_path = '/assets/OpenWeatherIcons/DefaultImageOW.png'

    # Return the determined icon path        
    return icon_path


def create_ow_weather_card(forecast, forecast_ow):
    """
    Creates a Dash html Div for a single forecast from OpenWeather.

    Args:
        forecast (dict): A dictionary containg the forecast data for a single time.
        forecast_ow (dict): The entire forecast data from OpenWeather.

    Returns:
        html.Div: A Dash html Div component.
    """
    # Retreive the time string from the forecast dictionary
    time_str = forecast.get('dt_txt', 'None')
    # Call the "format_time" function to format the time string
    formatted_time_ow = format_time(time_str, '%B %d, %Y, %I:%M %p')

    # Extract the weather informations
    description = forecast['weather'][0]['description']
    temp = forecast['main']['temp']
    feels_like = forecast['main']['feels_like']
    min_temp = forecast['main']['temp_min']
    max_temp = forecast['main']['temp_max']
    humidity = forecast['main']['humidity']

    # Extract the wind speed through the "dew_point" function
    dew_point_value = dew_point(forecast['main'])
    # Extract the wind speed through the "get_wind_speed" function
    wind_speed = get_wind_speed(forecast)
    # Extract the wind speed through the "get_visibility" function
    visibility = get_visibility(forecast)

    # Call the "extract_ow_icon_code" function to determine the file path for the appropriate weather icon based on the forecast data
    icon_path = extract_ow_icon_code(forecast, forecast_ow)
                    
    # Create and return the OpenWeather weather card as a html.Div component
    return html.Div( # Create the single weather card
        style={
            'border': '1px solid #0e0e0e',
            'borderRadius': '10px',
            'boxShadow': '2px 2px 8px rgba(0, 0, 0, 0.1)',
            'padding': '15px',
            'margin': '10px',
            'flexBasis': 'calc(33% - 20px)',
            'boxSizing': 'border-box',
            'display': 'inline-block',
            'fontFamily': 'Arial, sans-serif',
            'backgroundColor': '#f0f0f0'
        }, # Styles the appearance of the cards
        children=[
            html.H4(
                f'Time: {formatted_time_ow}',
                style={
                    'fontSize': '18px',
                    'marginBotom': '10px',
                    'color': '#2c3e50'
                }
            ),
            html.Img(
                src=icon_path,
                style={
                    'height': '80px',
                    'width': '80px'
                }
            ),
            html.P(f'Conditions: {description.title()}',
                style={
                    'fontSize': '17px',
                    'lineHeight': '1.4',
                    'fontFamily': 'Bahnschrift SemiBold'
                }
            ),
            html.Div( # Group the temperature related data - arranging verticaly
                style={
                    'display': 'flex', # Using a flex box
                    'flexDirection': 'column', # Stacking items vertically
                    'marginBottom': '8px' # Adding some space below
                },
                children=[
                    html.P(
                        f'Temperature: {temp}°F',
                        style={
                            'fontSize': '22px',
                            'fontWeight': 'bold',
                            'fontFamily': 'Eras Bold ITC'
                        }
                    ),
                    html.P(
                        f'Feels Like: {feels_like}°F',
                        style={
                            'fontSize': '17px',
                            'fontFamily': 'Berlin Sans FB'
                        }
                    ),
                    html.P(
                        f'Min Temperature: {min_temp}°F',
                        style={
                            'fontSize': '17px',
                            'fontFamily': 'Berlin Sans FB'
                        }
                    ),
                    html.P(
                        f'Max Temperature: {max_temp}°F',
                        style={
                            'fontSize': '17px',
                            'fontFamily': 'Berlin Sans FB'
                        }
                    ),
                ]
            ),
            html.P(
                f'Humidity: {humidity}%',
                style={
                    'fontSize': '20px',
                    'fontFamily': 'Colonna MT'
                }
            ),
            html.P(
                f'Dew Point: {dew_point_value:.2f}°F' if dew_point_value is not None else 'Dew Point: Not Available',
                
                style={
                    'fontSize': '16px',
                    'fontFamily': 'Maiandra GD'
                }
            ),
            html.Div( # Group the wind related data - arranging verically
                style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'marginBottom': '8px'
                },
                children=[
                    html.P(
                        f'Wind Speed: {wind_speed} m/s',
                        style={
                            'fontSize': '16px',
                            'fontFamily': 'Eras Medium ITC'
                        }
                    ),
                    html.P(
                        f'Visibility: {visibility} metres',
                        style={
                        'fontSize': '18px',
                        'fontFamily': 'High Tower Text'
                        }
                    ),
                ]
            ),
        ]
    )


def extract_ow_plotting_data(forecast_list):
    """
    Extracts time, temperaure, humidity, and wind speed from OpenWeather forecast data for plotting.

    Args:
        forecast_list (list): A list of forecast data from OpenWeather ("forecast_ow['list']").

    Returns:
        dict: A dictionary containing the list of times and corresponding temperatures, humidity, and wind speeds.
    """
    times = []
    temps = []
    humidity = []
    wind_speed = []
    dew_points = []

    if forecast_list: # Ensure forecast_list is not empty or None
        
        for forecast in forecast_list:
            time_str = forecast.get('dt_txt')
            if time_str:
                # Format the time for display
                formatted_time = format_time(time_str, '%Y-%m-%d %H:%M:%S')
                times.append(formatted_time)
                
                temps.append(forecast['main']['temp'])
                humidity.append(forecast['main']['humidity'])
                wind_speed.append(forecast['wind']['speed'])

                dew_point_value = dew_point(forecast['main'])
                dew_points.append(dew_point_value)
                
    return {'times': times, 'temp': temps, 'humidity': humidity, 'wind_speed': wind_speed, 'dew_points': dew_points}


def create_ow_graph(plotting_data, data_type):
    """
    Creates a Dash graph component to show OpenWeather temperature data against time.

    Args:
        plotting_data (dict): A dictionary containing "times", "temps", "humidity", and "wind_speed".
        data_type (str): The type of data to plot.

    Returns:
       dcc.Graph: A Dash graph component.
    """
    # Handle missing data
    # "plotting_data.get(data_type)" is used to safely check for the presence of the data associated with the requested "data_type"
    # Here, "data_type" is a variable that will hold strings like 'temp', 'humidity', and 'wind_speed'
    if not (plotting_data and plotting_data['times'] and plotting_data['temp'] and plotting_data.get(data_type)):
        return html.P(f'No data available for {data_type} graph.')

    # Extract the y-axis data
    # The "data_type" argument is used to access the corresponding list of values from the "plotting_data" dictionary
    y_data = plotting_data[data_type]
    # Select the title for the graph based on the "data_type"
    title = {
        'temp': 'Temperature Over Time',
        'humidity': 'Humidity Over Time',
        'wind_speed': 'Wind Speed Over Time',
        'dew_points': 'Dew Point Over Time'
    }.get(data_type, f'Over Time') # Default title for the graph

    # Set the title for y-axis
    y_title = {
        'temp': 'Temperature (°F)',
        'humidity': 'Humidity (%)',
        'wind_speed': 'Wind Speed (m/s)',
        'dew_points': ' Dew Point (°F)'
    }.get(data_type, '') # Default title for the y-axis
    color = {
        'temp': '#e84118',
        'humidity': '#00a8ff',
        'wind_speed': '#4cd137',
        'dew_points': '#f5cb11',
    }.get(data_type, '#30336b') # Default colour

    # Create the graph
    fig = go.Figure(
        # The "data" argument is a list containing the data to be plotted
        data=[
            go.Scatter(
                x=plotting_data['times'], # Set the x-axis to the list of times from the input data
                y=y_data,
                mode='lines+markers', # The graph should display both, lines connecting the data points and markers at the data points themselves
                line=dict(color=color, width=2),
                marker=dict(color=color, size=6)
            )
        ],
        # Design the layout
        layout=go.Layout(
            title=title,
            xaxis_title='Time',
            yaxis_title=y_title,
            template='plotly_white',
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray'),
        ),
    )
    # Return the Dash graph component
    return dcc.Graph(figure=fig)


def ow_data_processing(search_text):
    """
    Fetches and processes the weather data from OpenWeather.

    Args:
        search_text (str): The text entered in the search input box.

    Returns:
        list: A list of Dash HTML components to display the OpenWeather data.
    """
    # Fetch weather data from OpenWeather

    # Call the "get_coordinates" function to get the latitude and longitude of the location as specified by the "search_text"
    coordinates_ow = get_coordinates(search_text)
    
    # If "get_coordinates" function is successful it returns a tuple
    if coordinates_ow:
        latitude, longitude = coordinates_ow
        # Call the "get_weather_forecast_ow" function to get the forecast data from the obtained coordinates
        forecast_ow = get_weather_forecast_ow(latitude, longitude)
    # # If "get_coordinates" function fails it returns "None" and sets "forecast_ow" to "None"
    else:
        forecast_ow = None

    # Intitialize an empty list
    # This list will store the Dash HTML components that will be created to display the weather information
    children = []
    
    # Display the data obtained from OpenWeather
    if forecast_ow and forecast_ow['list']:

        # Process the forecast data for display
        forecast_list_ow = forecast_ow['list'][:9] # Limit the number of entries to the first 27 hours (in 3 hour intervals)

        # Create an empty list to store the created weather cards
        weather_cards_ow = []

        # Iterate through the forecast entries
        for forecast in forecast_list_ow:
            # Call the "create_ow_weather_card" for each entry to format the data for a single forecast into a displayable card (an "html.Div" element)
            # Append the created weather card to the "weather_cards_ow" list
            weather_cards_ow.append(create_ow_weather_card(forecast, forecast_ow))

        # After the loop, create the flex container with the desired number of cards
        # Append this container "html.Div" to the "children" list, to display the cards in the app's layout
        children.append(
            html.Div(
                style={
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'justifyContent': 'flex-start'
                }, # Styles the display area - to arrange the cards horizontally and wrap them to the next line if necessary
                # Set the "children" attribute of this container "html.Div" to the "weather_cards_ow" list
                # Which facilitates adding all the created weather cards to the container
                children = weather_cards_ow[:9]
            )
        )
        # Create and append the temperaure graph

        # Call the "extract_ow_plotting_data" to extract the data required for plotting
        plotting_data_ow = extract_ow_plotting_data(forecast_list_ow)
        # Call "create_ow_graph" to create the desired graphs
        # Append the generated graphs to the "children" list
        children.append(create_ow_graph(plotting_data_ow, 'temp'))
        children.append(create_ow_graph(plotting_data_ow, 'humidity'))
        children.append(create_ow_graph(plotting_data_ow, 'dew_points'))
        children.append(create_ow_graph(plotting_data_ow, 'wind_speed'))
        return children
    
    elif coordinates_ow is None:
        children.append(html.P(f'Could not retrieve coordinates for {search_text} from OpenWeather.\nPlease check your input!'))
    else:
        children.append(html.P('Sorry, could not retrieve weather data from OpenWeather!'))


# CATEGORY IV - Attributions for the Used Images


def load_image_attributions(source_select):
    """
    Loads the attribution data from a JSON file based on the selected source.

    Args:
        source_select (str): The selected weather source.

    Returns:
        If successful it returns a list of dictionaries containing the image attributions.
        otherwise returns an empty list to signal an error or that no data is available.
    """
    # Construct the filename
    filename = f'{source_select.lower()}_attributions.json'
    # Construct the filepath
    filepath = os.path.join('assets', 'Attributions', filename)
    
    try:
        # Load the JSON data
        with open(filepath, 'r') as f_attributions:
            return json.load(f_attributions)
        
    except FileNotFoundError:
        print(f'File not found! filename = {filename}, filepath = {filepath}\n\n')
        # If the file is not found, return an empty list
        return []
    except json.JSONDecodeError:
        print(f'Error: Invalid JSON format in the "{filename}".')
        # If the file contains invalid JSON data, return an empty list
        return []


def create_attribution_elements(attributions_list):
    """
    Create a list of Dash HTML elements to display the image attributions.

    Args:
        attributions_list (list): A list of dictiionaries, where each dictionary contains 'text' (the attribution text) and 'url' (URL of the image source) keys.

    Returns:
        list: A list of Dash HTML 'html.P' elements, each containing a 'html.A' element with the attribution information.
        Returns an empty list if the input list is empty or if any attribution dictionary is missing 'text' or 'url'.
    """
    # Create an empty list to hold the generated HTML eleemnts
    elements = []

    # Iterate through each item of the "attributions_list"
    for attributions in attributions_list:
        # Check if the current "attributions" dictionary contains the "text" and the "url" keys
        # If available, access the values associated with the respective keys
        if attributions.get('text') and attributions.get('url'):
            
            # Append the generated paragraph element to the "elements" list
            elements.append(
                html.P(
                    html.A(
                        attributions['text'],
                        href=attributions['url'],
                        target='_blank'
                    ),
                    style={
                        'fontSize': '12px'
                    }
                )
            )
            
    # Return the "elements" list        
    return elements


# CATEGORY V - User Interaction Callback
        
        
# '@app.callback()' - This is a decorator provided by Dash
# It links the output of a Python function ('update_search_output' - in this case) to a specific component property in the Dash app's layout
# And it also specifies which component property's change will trigger the function
@app.callback(
    # This part defines the output of the callback
    # 'search-output' - This refers to an "id" of a Dash HTML component that exists in the app's 'app.layout' block
    # 'children' - This specifies that the output of the 'update_search_output' function will update the "children" property of that HTML component
    # The 'children' property typically holds the content displayed within a HTML element
    
    [ # This part defines the OUTPUTS of the callback function
        Output('search-output', 'children'), # 1. Updates the children of the "search_output" div
        Output('aw-attribution', 'children'), # 2. Updates the Accuweather attribution
        Output('ow-attribution', 'children'), # 3. Updates the Openweather attribution
        Output('attributions-container', 'className'), # 4. Updates the CSS class of the attributions container
        Output('attributions-content', 'children'), # 5. Updates the children (contents within the attribution section)of the attributions content
        Output('attributions-content', 'style'), # 6. Updates the inline styles of the attributions content
        Output('attributions-button', 'style'), # 7. Updates the inline styles of the button that toggles the visibility of the attributions
        Output('attributions-visibility', 'data') # 8. Updates the stored visibility data 
    ],
    
    # This part of the decorator defines the input that triggers the callback
    # 'search-button-image' - This refers to the "id" of the "html.Img" component that represents the search button image
    # 'n_clicks':
    #   This is the property of the "html.Img" component. Every clickable Dash component has the "n_clicks" property
    #   It starts at 'None', and then every time the component is clicked 'n_clicks' increases by one
    # The first "Input" means: The callback function will run every time the search button image is clicked
    # The second "Input" makes that text available to the callback function
    # The second "Input" calls the "update_search_output" function whenever the user changes the selected source
    
    [ # This part defines the INPUTS of the callback function
        Input('search-button-image', 'n_clicks'), # 1. Triggered when the search button is clicked
        Input('source-select', 'value'), # 2. Triggered when the weather source is changed
        Input('attributions-button', 'n_clicks') # 3. Triggered when attribution accordion (the button to show the image attributions) is clicked
    ],

    # State is used to pass along the current value of a component to the callback function without triggering the callback itself
    # While "Input" does trigger the callback whenever its value changes, but "State" provides the contextual information to the callback
    # Usage of "State":
    #   "State" is used when an information is needed from a particular component to perform a specific action
    #    But the action should occur only when triggered by a change in an "Input" component's property and not because the "State" value changed
    # Change to a "State" component's property will not trigger the callback, it will only provide the current value when the callback is triggered by an "Input"
    
    [ # This part defines the ADDITIONAL INPUTS (STATE) of the callback function
        State('search-input', 'value'), # 1. The current value of the search input
        State('attributions-visibility', 'data'), # 2. The current visisbility state of the attributions
    ],
        
)
def update_all_outputs(
    n_clicks,
    source_select,
    attribution_clicks,
    search_value,
    visibility_data,
):
    """
    Updates the app's output components in response to user interactions such as searching, selecting a weather source, or toggling the visibility of the image
    attributions section.

    Args:
        n_clicks (int): The number of times the search button has been clicked.
        source_select (str): The currently selected weather source.
        attribution_clicks (int): The number of times the attributions button (Sources and Attribution Details for Images - button) was clicked.
        search_value (str): The text entered in the search input box.
        visibility_data (dict): A dictionary storing the visibility state of the attributions section.

    Returns:
        tuple: A tuple containing the updated values for the output components -
                    search_results (list): Updated weather cards and graphs.
                    aw_attribution (html.Div): Updated AccuWeather attribution.
                    ow_attribution (html.Div): Updated OpenWeather attribution.
                    container_class (str): CSS class for the attributions container.
                    attribution_elements (list): A list of HTML elements for the attributions content.
                    content_style (dict): Style for the attributions content (to show or hide).
                    button_style (dict): Style for the attributions button (to show or hide).
                    visibility_data (dict): Updated visibility state of the attributions.
    """
    # This Dash object provides information about - what caused the callback to run
    ctx = dash.callback_context
    # Extract the "id" of the component that triggered the callback
    # "ctx.triggered" - It is a list of dictionaries, each describing an "Input" which triggered the callback and their "id" in a key "prop_id"
    # "ctx.triggered[0]['prop_id']" - "ctx.triggered[0]": Accesses the first dictionary in the list and the "prop_id" (e.g., "search-button-image.n_clicks")
    # ".split('.')" - Splits the "prop_id" string by "." creating a list (e.g., ['search-button-image', 'n_clicks'])
    # "[0]" - Extracts the first element of the splitted list i.e., the component's ID
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Set a default value to the "visibility_data" if it is initially 'None'
    visibility_data = visibility_data or {'is_visible': False}
    # Extract the current visibility state of the attribution section
    is_visible = visibility_data['is_visible']

    # Initialize the "aw_attribution"
    aw_attribution = None
    # Initialize the "ow_attribution"
    ow_attribution = None
    # Initialize the attribution elements
    attribution_elements = []

    # Set the initial CSS class for the "html.Div" element with the ID "accordion-container"
    # The class "accordion-container" (present in the "style.css" file) is responsible for the basic layout of the attribution section
    container_class = 'accordion-container'
    # Directly set the inline "style" property of the "html.Div" element with ID "accordion-container"
    # "'display': 'none'" - Hides this "html.Div" element which contains the contents of the accordion (attributions for the images)
    content_style = {'display': 'none'}
    # Set the style for the "html.Button" element with the ID "accordion-button"
    button_style = {
        'display': 'none', # Initially hide the button
        'cursor': 'pointer',
        'textAlign': 'center',
        'width': 'auto'
    }

    # Initialize the "search_results"
    search_results = None

    # This block handles the intial rendering of the app when no user interactions have occured
    # When the app first loads, no component has triggered the callback, so "ctx.triggered" is empty
    if not ctx.triggered:
        # The "update_all_outputs" function has to update multiple components throughout the app
        # Therefore it must return a value for every "Output" in the "@app.callback" decorator
        return ( # Handles the initial load of the app
            # Ensure that the search results are cleared even on the initial load or when the callback is triggered without a search
            # This will provide a consistent behaviour for the loading animation
            None, # Corresponds to "Output('search-output', 'children')" 
            None, # Corresponds to "Output('aw-attribution', 'children')"
            None, # Corresponds to "Output('ow-attribution', 'children')"
            container_class, # ("accordion-container") Set the initial CSS class for the attribution container
            [], # (An empty list) Set the initial content of the attribution content area to empty
            content_style, # ({'display': 'none'}) - Hide the attribution content by default
            button_style, # ('display': 'none') - Hide the button that toggles the attribution section
            {'is_visible': False} # Set the initial state of attribution section's visibility to 'hidden' in the "dcc.Store" component ("attributions-visibility")
        )
    # Fetch and display the weather data based on user input
    elif trigger_id == 'search-button-image' or (trigger_id == 'source-select' and search_value):
        # Ensure:
        # That the search button has been clicked at least once ("n_clicks > 0") and there is a value in the search box ("search_value")
        # "n_clicks is not None" - Prevents error on initial load
        if n_clicks is not None and n_clicks > 0 and search_value:

            try:
                
                if source_select == 'aw':
                    # Call the "aw_data_processing" function to fetch and format the data from AccuWeather
                    search_results = aw_data_processing(search_value)
                    # Construct and display the AccuWeather logo
                    aw_attribution = html.Div(
                        [
                            html.A(
                                html.Img(
                                    src='/assets/Image/AW_RGB_R.png',
                                    alt='AccuWeather',
                                    style={
                                        'height': '40px'
                                    }
                                ),
                                href='https://www.accuweather.com/',
                                target='_blank'
                            )
                        ],
                        style={
                            'textAlign': 'center',
                            'marginTop': '5px',
                            'marginBottom': '5px'
                        }
                    )
                    # Ensure only the correct weather source's attribution is displayed
                    ow_attribution = None
                    
                elif source_select == 'ow':
                    # Call the "ow_data_processing" function to fetch and format the data from OpenWeather
                    search_results = ow_data_processing(search_value)
                    # Construct and display the OpenWeather attribution
                    ow_attribution = html.Div(
                        html.P(
                                [
                                    'Weather data provided by ',
                                    html.A(
                                        'OpenWeather',
                                        href='https://www.openweathermap.org',
                                        target = '_blank'
                                    ),
                                    ' (',
                                    html.A (
                                        'CC BY-SA 4.0',
                                        href='https://creativecommons.org/licenses/by-sa/4.0/',
                                        target='_blank',
                                    ),
                                    ')',
                                ],
                                style={
                                    'fontSize': '12px',
                                    'color': '#333333',
                                    'textAlign': 'center',
                                    'marginTop': '5px',
                                    'marginBottom': '5px'
                                }
                            )
                    )
                    # Ensure only the correct weather source's attribution is displayed
                    aw_attribution = None

                if search_results:
                    # If the weather data is successfully retrieved
                    # "container_class = ..." - Set up the CSS class for the attribution container
                    container_class = 'accordion-container'
                    # "content_style = ..." - Hide the attribution content initially
                    content_style = {'display': 'none'}
                    # "button_style = ..." - Display the button that allows the user to toggle the attribution's visibility
                    button_style = {
                        'display': 'block',
                        'cursor': 'pointer',
                        'textAlign': 'center',
                        'width': '100%'
                    }
                else:
                    # If there was an error fetching the weather data
                    # "container_class = ..." - Set up the CSS class for the attribution container
                    container_class = 'accordion-container'
                    # "content_style = ..." - Hide the attribution content
                    content_style = {'display': 'none'}
                    # "button_style = ..." - Hide the attribution button
                    button_style = {
                        'display': 'none',
                        'cursor': 'pointer',
                        'textAlign': 'center',
                        'width': '100%'
                    }
                # Return the updated data for all the "Output" components including the weather results, attributions, and styling for the attribution section
                return ( # This "return" executes when the user performs a search and the data is successfully fetched
                    search_results, # Updated weather information (weather cards) and graphs
                    aw_attribution, # Updated AccuWeather attribution
                    ow_attribution, # Updated OpenWeather attribution
                    container_class, # Sets the CSS class for theh container of the attribution section
                    attribution_elements, # List of the HTML elements containing the attribution information
                    content_style, # Sets the CSS "style" for the content area of the attribution section (attributions-content)
                    button_style, # Sets the CSS "style" for the button that toggles the visibility of the attribution content (attributions-button)
                    {'is_visible': is_visible} # Updates the stored state of wheather the attribution section is currently visible or not
                )
            
            except Exception as e:
                print(f'Encountered an error during fetching data!\nDetails: {e}')
                return ( # This "return" handles errors during data fetching
                    None,
                    None,
                    container_class,
                    attribution_elements,
                    content_style,
                    button_style,
                    {'is_visible': is_visible}
                )
            
            finally:
                # This "return" always executes after the "try" or "except" block
                # And ensures that the loading animation is hidden and that all output components are updated, even if there was an error
                return (
                    search_results,
                    aw_attribution,
                    ow_attribution,
                    container_class,
                    attribution_elements,
                    content_style,
                    button_style,
                    {'is_visible': is_visible}
                )
        
        # Handle the case when the search button has not been clicked or the search value is empty
        else:
            # "container_class = ..." - Set up the CSS class for the attribution container
            container_class = 'accordion-container'
            # "content_style = ..." - Hide the content area of the attribution section
            content_style = {'display': 'none'}
            # "button_style = ..." - Hide the attribution button
            button_style = {
                'display': 'none',
                'cursor': 'pointer',
                'textAlign': 'center',
                'width': '100%'
            }
            # Return the default or empty states for the "Outputs" when the search button is triggered without a search value
            # Or potentially on initial load after the first block ('first block' - the "if not ctx.triggered:" block)
            return( # This "return" handles the case where the search button is clicked but the search value is empty
                # Ensure that the search results are cleared even on the initial load or when the callback is triggered without a search
                # This will provide a consistent behaviour for the loading animation
                None, # Clear the 'search-output' - Output('search-output', 'children')
                None, # Clear the AccuWeather attribution
                # Tell Dash not to update the 'ow-attribution' component
                # Likely because:
                #   The attribution might have been set by a previous search
                #   And clearing it is unnecessary if the search button has not been clicked or the search bar is empty
                dash.no_update,
                container_class, # Reset the CSS class of the attribution container
                [], # Clear any content that might have been in the attribution content area
                content_style, # Ensure that the attribution content remains hidden
                button_style, # Ensure that the button to toggle the attribution remains hidden
                {'is_visible': False} # Reset the visibility state of the attribution section in the "dcc.Store"
            )
        
    # Check if the component that triggered the callback is "dcc.Dropdown" with the ID "source-select" - meaning the user has changed the selected weather source
    # And also check ('and not search_value') if the "search-input" box is empty or not
    # This whole condition checks if the user has changed the weather source in the "dcc.Dropdown", but the search input box is empty
    elif trigger_id == 'source-select' and not search_value:
        # Set the CSS class of the "html.Div" with the ID "attributions-container" to "accordion-container"
        container_class = 'accordion-container'
        content_style = {'display': 'none'} # Hide the attribution content
        button_style = { # Hide the attribution button
            'display': 'none',
            'cursor': 'pointer',
            'textAlign': 'center',
            'width': '100%'
        }
        return( # This "return" handles the case where the source select dropdown is changed, but the search value is empty
            None, # Clear the "search-output" div
            None, # Clear the AccuWeather attribution
            dash.no_update, # Tell Dash not to update the "ow-attribution"
            container_class, # Update the CSS class of the attribution container
            [], # Clear any content that might be present the attribution content area
            content_style, # Hide the attribution content
            button_style, # Hide the attribution button
            {'is_visible': False} # Reset the visibility state of the attribution section to hidden
        )
    
    # Check if the component that triggered the callback is the button with the ID "attributions-button"    
    elif trigger_id == 'attributions-button':
        # Toggle the value of the 'is_visible' variable.
        # If the attribution section was hidden (i.e., 'is_visible' was set to False), set the 'is_visible' to True, and vice-versa 
        is_visible = not is_visible

        # Initialize attribution_elements (an empty list)
        # This list will hold the Dash HTML components that display the attribution information
        attribution_elements = []

        # Handle the visibility of the attributions section (i.e., 'is_visible' is True)
        if is_visible:
            if source_select == 'aw':
                # Call the "load_image_attributions" function to load the attribution data from a JSON file
                attributions_data = load_image_attributions('aw')
            elif source_select == 'ow':
                # Call the "load_image_attributions" function to load the attribution data from a JSON file
                attributions_data = load_image_attributions('ow')
            # Ensure that the "attribution_data" is loaded successfully
            if attributions_data:
                # Call the "create_attribution_elements" function to generate a list of Dash HTML "html.P" and "html.A" components from the data
                attribution_elements = create_attribution_elements(attributions_data)
            else:
                attribution_elements = [html.P('No attribution data is available')]
                
            # Update the CSS class of the attribution container to "accordion-container show" (the "show" class is used to expand the accordion)
            container_class = 'accordion-container show'
            content_style = {'display': 'block'} # Display the attribution content
            button_style = { # Display the attribution button
                'display': 'block',
                'cursor': 'pointer',
                'textAlign': 'center',
                'width': '100%'
            }
            
        # Reset the attribution section to its hidden state    
        else:
            container_class = 'accordion-container' # Set the CSS class of the attribution container to its default state, which is not to show the expanded content
            content_style = {'display': 'none'} # Ensure that the attribution content area is hidden
            button_style = { # Set the style of the button
            'display': 'block',
            'cursor': 'pointer',
            'textAlign': 'center',
            'width': '100%'
        }
    
        # Return a tuple with the updated states for the "Output" components
        return( # This "return" handles the toggling of the attribution section's visibility
            dash.no_update, # Tell Dash to not update the search result
            dash.no_update, # Tell Dash to not update the "aw-attribution"
            dash.no_update, # Tell Dash to not update the "ow-attribution"
            container_class, # Update the CSS class to show or hide the attribution content
            attribution_elements, # List of the HTML elements containing the attribution information
            content_style, # Style to show or hide the attribution content
            button_style, # Style to show the attribution button
            {'is_visible': is_visible} # Update the visibility state in the "dcc.Store" component
        )
