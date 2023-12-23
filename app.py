from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# validate the form and return the results
def validate_form(startdate, enddate):
    #check if the user entered a start date and end date
    if startdate and enddate:
        #check if the end date is after the start date
        print(startdate)
        if startdate > enddate:
            return render_template('index.html', error='End date should be after start date')
        else:
            return True


@app.route('/search', methods=['POST','GET'])
def search():
    if request.method == 'POST':
        city = request.form['city']
        StartDateTime	 =  request.form['startdate']
        EndDateTime = request.form['enddate']
        Artist = request.form['artist']
        api_key = 'vloAti78R5VU5xlEehviuY4dgV7MWIsj'  # Replace with your actual API key
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}&city={city}'
        if StartDateTime:
            StartDateTime += 'T00:00:00Z'
            url += f'&startDateTime={StartDateTime}'
        if EndDateTime:
            EndDateTime += 'T23:59:59Z'
            url += f'&endDateTime={EndDateTime}'
        validate_form(StartDateTime, EndDateTime)
        if Artist:
            url += f'&keyword={Artist}'

        response = requests.get(url)
        if response.status_code == 200:
            print(response.json())
            events = response.json().get('_embedded', {}).get('events', [])
            return render_template('results.html', events=events)
        else:
            return 'Error: Unable to fetch events', 500

if __name__ == '__main__':
    app.run(debug=True)
