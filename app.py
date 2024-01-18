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
        if startdate > enddate:
            return False
        else:
            return True
    else:
        return True
        
#process raw data for single event (for /discovery/v2/events/{id} )
def process_single_event_data(raw_event_data):
      event_details = {
        'name': raw_event_data.get('name', ''),
        'id': raw_event_data.get('id', ''),
        'url': raw_event_data.get('url', ''),
        'locale': raw_event_data.get('locale', ''),
        'pleaseNote': raw_event_data.get('pleaseNote', ''),
        'images': [image['url'] for image in raw_event_data.get('images', [])],
        'url': raw_event_data.get('url', ''),
        'sales': {
            'startDateTime': raw_event_data.get('sales', {}).get('public', {}).get('startDateTime', ''),
            'endDateTime': raw_event_data.get('sales', {}).get('public', {}).get('endDateTime', ''),
            'startTBA': raw_event_data.get('sales', {}).get('public', {}).get('startTBA', ''),
            'startTBD': raw_event_data.get('sales', {}).get('public', {}).get('startTBD', '')
        },
        'dates': {
            'localDate': raw_event_data.get('dates', {}).get('start', {}).get('localDate', ''),
            'localTime': raw_event_data.get('dates', {}).get('start', {}).get('localTime', ''),
            'dateTime': raw_event_data.get('dates', {}).get('start', {}).get('dateTime', ''),
            'timezone': raw_event_data.get('dates', {}).get('timezone', ''),
            'status': raw_event_data.get('dates', {}).get('status', {}).get('code', '')
        },
        'priceRanges': [{
            'type': price_range.get('type', ''),
            'currency': price_range.get('currency', ''),
            'min': price_range.get('min', 0),
            'max': price_range.get('max', 0)
        } for price_range in raw_event_data.get('priceRanges', [])],
        'seatmapUrl': raw_event_data.get('seatmap', {}).get('staticUrl', '')
        }

      # Parsing venue details
      venue_info = raw_event_data.get('_embedded', {}).get('venues', [{}])[0]
      raw_event_data['venue'] = {
          'name': venue_info.get('name', ''),
          'url': venue_info.get('url', ''),
          'address': venue_info.get('address', {}).get('line1', ''),
          'city': venue_info.get('city', {}).get('name', ''),
          'countryCode': venue_info.get('country', {}).get('countryCode', ''),
          'generalInfo': venue_info.get('generalInfo', {}).get('generalRule', ''),
          'accessibleSeatingDetail': venue_info.get('accessibleSeatingDetail', ''),
          'boxOfficeInfo': venue_info.get('boxOfficeInfo', {}).get('openHoursDetail', ''),
          'generalInfo': venue_info.get('generalInfo', {}).get('generalRule', ''),
          'parkingDetail': venue_info.get('parkingDetail', ''),
      }        
      # Parsing attraction details
      attraction_info = raw_event_data.get('_embedded', {}).get('attractions', [{}])[0]
      event_details['attraction'] = {
      'name': attraction_info.get('name', ''),
      'url': attraction_info.get('url', ''),
      'images': [image['url'] for image in attraction_info.get('images', [])]
      }
      event_details['accessibility'] = raw_event_data.get('accessibility', {}).get('ticketLimit', '')
      event_details['ageRestrictions'] = raw_event_data.get('ageRestrictions', {}).get('legalAgeEnforced', '')
      print(event_details)
      print(venue_info)
      return event_details, venue_info


# Process raw data for all events (for /discovery/v2/events )
def process_event_data(raw_event_data):
    if not raw_event_data:
        return None
    events = raw_event_data.get('_embedded', {}).get('events', [])
    processed_events = []
    for event in events:
        processed_event = {}
        processed_event['id'] = event.get('id', '#')
        processed_event['name'] = event.get('name', '#')
        processed_event['url'] = event.get('url', '')
        processed_event['start_date'] = event.get('dates', {}).get('start', {}).get('localDate', '')
        processed_event['start_time'] = event.get('dates', {}).get('start', {}).get('localTime', '')
        processed_event['venue'] = event.get('_embedded', {}).get('venues', [{}])[0].get('name', '')
        processed_event['city'] = event.get('_embedded', {}).get('venues', [{}])[0].get('city', {}).get('name', '')
        processed_event['state'] = event.get('_embedded', {}).get('venues', [{}])[0].get('state', {}).get('name', '')
        processed_event['postal_code'] = event.get('_embedded', {}).get('venues', [{}])[0].get('postalCode', '')
        processed_event['country'] = event.get('_embedded', {}).get('venues', [{}])[0].get('country', {}).get('name', '')
        processed_event['timezone'] = event.get('_embedded', {}).get('venues', [{}])[0].get('timezone', 'TBD')
        processed_event['keyword'] = event.get('_embedded', {}).get('attractions', [{}])[0].get('name', 'TBD')
        processed_event['image'] = event.get('images', [{}])[0].get('url', 'TBD')
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
    response = requests.get(url, allow_redirects=True)
    if response.status_code == 200:
        return process_event_data(response.json())
    else:
        return response.status_code

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
    # get top 10 events from ticketmaster
    url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}'
    events = request_api(url)
    if isinstance(events, list):    
        return render_template('index.html', events=events, cities=cities, venues=venues, artists=artists)
    else:
        flash("Something is wrong with the Ticketmaster Api response code", events)  # Flashing an error message

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
        if isinstance(events, list):
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
        if isinstance(events, list):
            return render_template('results.html', events=events,cities=cities, venues=venues, artists=artists)
        else:
            flash("API request failed. Response code: {}".format(events))
            return redirect(url_for('index'))

# app route for event details
@app.route('/event/<id>', methods=['POST','GET'])
def event(id):
    url = f'https://app.ticketmaster.com/discovery/v2/events/{id}.json?apikey={api_key}'
    response = requests.get(url, allow_redirects=True)
    if response.status_code == 200:
        event_details= response.json()
        return jsonify(event_details)
    else:
        return jsonify({"error": "Error with Ticketmaster API", "status_code": response.status_code}), 400
    
if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    app.run(debug=True)
    profiler.disable()
    profiler.print_stats(sort='cumulative')