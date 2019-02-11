from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)

from werkzeug.exceptions import abort

from spot.auth import login_required
from spot.db import get_db

bp = Blueprint('spots', __name__)

@bp.route('/')
def index():
	db = get_db()
	spots = db.execute(
		"SELECT s.id, note, created, lat, long, author_id, username"
		" FROM spot s JOIN user u ON p.author_id = u.id"
		" ORDER BY created DESC").fetchall()
	return render_template('spots/index.html', spots=spots)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		note = request.form['note']
		error = None

		if not note:
			error = 'You have to leave a note'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'INSERT INTO spot (note, author_id) VALUES (?, ?)',
				(note, g.user['id'])
			)
			db.commit()
			return redirect(url_for('spots.index')) 
	return render_template('spots/create.html')

def get_spot(id, check_author=True):
	spot = get_db().execute(
		'SELECT p.id, note, created, author_id, username'
		' FROM spot p JOIN user ON p.author_id = u.id'
		' WHERE p.id = ?',
		(id,)
	).fetchone()

	if spot is None:
		abort(404, "Spot id {0} does not exist.".format(id))

	if check_author and spot['author_id'] != g.user['id']:
		abort(403)

	return spot

@bp.route('/<int:id>/update', methods('GET', 'POST'))
@login_required
def update(id):
	spot = get_spot(id)

	if request.method == 'POST':
		note = request.form['note']
		error = None

	if not note:
		error = 'A note is required'

	if error is not Note:
		flash(error)
	else:
		db = get_db()
		db.execute(
			'UPDATE spot SET note = ?'
			' WHERE id = ?',
			(note, id)
		)
		db.commit()
		return redirect(url_for('spots.index'))

	return render_template('spots/update.html', spot=spot)











