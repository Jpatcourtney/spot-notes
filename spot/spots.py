from flask import (Blueprint, flash, g, current_app, redirect, render_template, request, url_for)

from werkzeug.exceptions import abort
import datetime
import requests

from spot.auth import login_required
from spot.db import get_db

bp = Blueprint('spots', __name__)

#########
#       #
# VIEWS #
#       #
#########

# Renders index template
@bp.route('/')
def index():
	if g.user:
		api_key = current_app.config['TZ_API_KEY']
		db = get_db()
		spots = db.execute(
			"SELECT p.id, note, local_time, lat, lng, author_id, username"
			" FROM spot p JOIN user u ON p.author_id = u.id"
			" WHERE u.id = ?"
			" ORDER BY created DESC",(g.user['id'],)
		).fetchall()

		return render_template('spots/index.html', spots=spots, api_key=api_key)
	else:
		return render_template('spots/index.html')

# Passes full list of notes to template
@bp.route('/spots')
def spots():
	db = get_db()
	spots = db.execute(
		"SELECT p.id, note, local_time, lat, lng, author_id, username"
		" FROM spot p JOIN user u ON p.author_id = u.id"
		" WHERE u.id = ?"
		" ORDER BY created DESC",(g.user['id'],)
	).fetchall()
	return render_template('spots/spots.html', spots=spots)

# Get Selects spot by ID and renders template
@bp.route('/<int:id>/')
@login_required
def spot(id):
	spot = get_spot(id)
	api_key = current_app.config['TZ_API_KEY']

	return render_template('spots/spot.html', spot=spot, api_key=api_key)

# Get renders template with form
# Post get UTC & local time. Inserts note to database. Redirects to index.
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		note = request.form['note']
		lat = request.form['lat']
		lng = request.form['lng']
		created = datetime.datetime.utcnow()
		utc_offset = get_utc_offset(lat, lng, created)
		local_time = created + datetime.timedelta(seconds=utc_offset)
		error = None

		if not note:
			error = 'You have to leave a note'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'INSERT INTO spot (note, author_id, lat, lng, created, local_time)'
				' VALUES (?, ?, ?, ?, ?, ?)',
				(note, g.user['id'], lat, lng, created, local_time)
			)
			db.commit()
			return redirect(url_for('spots.index')) 
	return render_template('spots/create.html')

# Get Spot from database and renders form
# Post Updates note for record.
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
	spot = get_spot(id)

	if request.method == 'POST':
		note = request.form['note']
		error = None

		if not note:
			error = 'A note is required'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'UPDATE spot SET note = ?'
				' WHERE id = ?',
				(note, id)
			)
			db.commit()
			return redirect(url_for('spots.spot', id=id))

	return render_template('spots/update.html', spot=spot)

# Post only, Deletes record from database. No template.
@bp.route('/<int:id>/delete', methods=("POST",))
@login_required
def delete(id):
	get_spot(id)
	db = get_db()
	db.execute('DELETE FROM spot WHERE id = ?', (id,))
	db.commit()
	return redirect(url_for('spots.spots'))

#############
#           #
# FUNCTIONS #
#           #
#############

# Takes Spot ID and returns record
def get_spot(id, check_author=True):
	spot = get_db().execute(
		'SELECT p.id, note, lat, lng, local_time, created, author_id, username'
		' FROM spot p JOIN user u ON p.author_id = u.id'
		' WHERE p.id = ?',
		(id,)
	).fetchone()

	if spot is None:
		abort(404, "Spot id {0} does not exist.".format(id))

	if check_author and spot['author_id'] != g.user['id']:
		abort(403)

	return spot

# Takes lat, lng and UTC and returns the local time.
# Uses Google TimeZone API
def get_utc_offset(lat, lng, utc_time):
	url = 'https://maps.googleapis.com/maps/api/timezone/json?location={0},{1}&timestamp={2}&key={3}'
	utc_timestamp = utc_time.timestamp()
	api_key = current_app.config['TZ_API_KEY']

	api_response = requests.get(url.format(lat,lng,utc_timestamp,api_key))
	response_dict = api_response.json()

	dst_offset = response_dict['dstOffset']
	raw_offset = response_dict['rawOffset']
	utc_offset = dst_offset + raw_offset
	return utc_offset











