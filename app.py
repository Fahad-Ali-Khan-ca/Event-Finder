from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    city = request.args.get('city')  # Get city from user input
    api_key = 'vloAti78R5VU5xlEehviuY4dgV7MWIsj'  # Replace with your actual API key
    url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}&city={city}'
    print('city: ', city)

    response = requests.get(url)
    if response.status_code == 200:
        events = response.json().get('_embedded', {}).get('events', [])
        return render_template('results.html', events=events, city=city)
    else:
        return 'Error: Unable to fetch events', 500

if __name__ == '__main__':
    app.run(debug=True)
