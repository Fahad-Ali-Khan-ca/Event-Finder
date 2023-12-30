from flask import Flask, render_template, request,redirect,url_for,flash
import requests
import json
import os
from flask import jsonify
import cProfile

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
api_key = 'vloAti78R5VU5xlEehviuY4dgV7MWIsj'  
url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}'





# ==================== FUNCTIONS ====================

# Ensure start date is before end date
def validate_form(startdate, enddate):
    if startdate and enddate:
        print(startdate)
        if startdate > enddate:
            return False
        else:
            return True
    else:
        return True
        
# Process raw event data
def process_event_data(raw_event_data):
    events = raw_event_data.get('_embedded', {}).get('events', [])
    processed_events = []
    for event in events:
        processed_event = {}
        processed_event['name'] = event.get('name', '#')
        processed_event['url'] = event.get('url')
        processed_event['start_date'] = event.get('dates', {}).get('start', {}).get('localDate', '')
        processed_event['start_time'] = event.get('dates', {}).get('start', {}).get('localTime', '')
        processed_event['venue'] = event.get('_embedded', {}).get('venues', [{}])[0].get('name', '')
        processed_event['city'] = event.get('_embedded', {}).get('venues', [{}])[0].get('city', {}).get('name', '')
        processed_event['state'] = event.get('_embedded', {}).get('venues', [{}])[0].get('state', {}).get('name', '')
        processed_event['postal_code'] = event.get('_embedded', {}).get('venues', [{}])[0].get('postalCode', '')
        processed_event['country'] = event.get('_embedded', {}).get('venues', [{}])[0].get('country', {}).get('name', '')
        processed_event['timezone'] = event.get('_embedded', {}).get('venues', [{}])[0].get('timezone', '')
        processed_event['keyword'] = event.get('_embedded', {}).get('attractions', [{}])[0].get('name', '')
        processed_event['image'] = event.get('images', [{}])[0].get('url', '')
        if processed_event['url'] != None:
            processed_events.append(processed_event)
    return processed_events

#parser function for names  from json files
def parse_data_json(file):
    file_path = os.path.join(app.static_folder, 'data', file)
    with open(file_path) as file:
        data = json.load(file)
        list = []
        for name  in data:
            list.append(name['name'])
    return list

#function for request to ticketmaster api
def request_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        return process_event_data(response.json())
    else:
        print(f"API request failed with status code {response.status_code}: {response.text}")
        return None

#========================================Global Data===============================================================
cities = []
venues = []
artists = []
cities = parse_data_json('cities.json')
venues = parse_data_json('venues.json')
artists = parse_data_json('artists.json')



# ==================== ROUTES ====================

# return home page with city list and venue list and artist list 
@app.route('/')
def index():
    return render_template('index.html', cities=cities, venues=venues, artists=artists)


@app.route('/search', methods=['POST','GET'])
def search():
    if request.method == 'POST':
        city = request.form['city']
        StartDateTime	 =  request.form['startdate']
        EndDateTime = request.form['enddate']
        Keyword = request.form['keyword']
        api_key = 'vloAti78R5VU5xlEehviuY4dgV7MWIsj'  
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}'
        if city:
            url += f'&city={city}'
        if StartDateTime:
            url += f'&startDateTime={StartDateTime}T00:00:00Z'
        if EndDateTime:
            url += f'&endDateTime={EndDateTime}T23:59:59Z'
        if Keyword:
            url += f'&keyword={Keyword}'

        # Validate form
        if not validate_form(StartDateTime, EndDateTime):
            flash("Error: Start date must be before end date.")
            return redirect(url_for('index'))

        # Request API
        events = request_api(url)
        if events:
            return render_template('results.html', events=events, cities=cities, venues=venues, artists=artists)
        else:
            flash("Error: something went wrong.", "error")
            return redirect(url_for('index'))


@app.route('/Nav/<name>/<id>', methods=['POST','GET'])
def Nav_city(name, id):
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}'
        if id != 'city':
            url += f'&keyword={name}'
        else:  
            url += f'&city={name}'
        events = request_api(url)
        if events:
            return render_template('results.html', events=events,cities=cities, venues=venues, artists=artists)
        else:
            flash("Couldn't get data")  # Flashing an error message
            return redirect(url_for('index'))
  

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    app.run(debug=True)
    profiler.disable()
    profiler.print_stats(sort='cumulative')