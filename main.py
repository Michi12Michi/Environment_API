from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import datetime
import requests
import json
import os

API_URL = "https://api.api-ninjas.com/v1/airquality"
API_KEY = os.environ.get("API_KEY")
HEADER = {"X-Api-Key": API_KEY}
app = Flask(__name__)
# use a custom string instead of os.environ.get("APPKEY")
app.secret_key = os.environ.get("APPKEY")
bs = Bootstrap5(app)

class CityForm(FlaskForm):
    latitude = StringField("Latitude", render_kw={'style': 'color: #000000'}, validators=[DataRequired()])
    longitude = StringField("Longitude", validators=[DataRequired()])
    submit = SubmitField()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/search', methods=["GET", "POST"])
def search():
    form = CityForm()
    form_data = []
    if form.validate_on_submit():
    	curr_datatime = datetime.datetime.now()
    	parameters = {"lat": form.latitude.data, "lon": form.longitude.data}
    	resp = requests.get(API_URL, params = parameters, headers = HEADER)
    	resp.raise_for_status()
    	api_data = resp.json()
    	final_data = {
			"day": curr_datatime.day,
			"month": curr_datatime.month,
			"year": curr_datatime.year,
			"latitude": parameters["lat"],
			"longitude": parameters["lon"],
			"co": api_data["CO"]["concentration"],
			"no2": api_data["NO2"]["concentration"],
			"o3": api_data["O3"]["concentration"],
			"so2": api_data["SO2"]["concentration"],
			"pm25": api_data["PM2.5"]["concentration"],
			"pm10": api_data["PM10"]["concentration"]
    	}
    	try:
    		with open("data.json", "r") as fd:
    			old_data = json.load(fd)
    	except FileNotFoundError:
    		with open("data.json", "w") as fd:
    			form_data.append(final_data)
    			json.dump(form_data, fd, indent = 4)
    	else:
    		old_data.append(final_data)
    		with open("data.json", "w") as fd:
    			json.dump(old_data, fd, indent = 4)
    	return render_template("results.html", item = final_data)
    return render_template("search.html", form=form)

@app.route('/recent')
def recent_searches():
	try:
		with open("data.json", "r") as fd:
			old_data = json.load(fd)
	except FileNotFoundError:
		return render_template("index.html")
	else:
		return render_template('recent.html', results = old_data)
	return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
