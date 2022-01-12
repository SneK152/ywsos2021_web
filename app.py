from flask import Flask, render_template, jsonify, request, redirect, session, abort, flash
from flask_session import Session
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import pymongo
import os
from config import Config, db
import datetime
import jwt
import bson
from functools import wraps
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timezone, timedelta
from werkzeug.utils import secure_filename
from uuid import uuid4
from geopy.geocoders import Nominatim
from flask_minify import minify
import rcssmin
import timeago
from werkzeug.utils import safe_join
import hashlib
import contextlib


class AddStaticFileHashFlask(Flask):
    def __init__(self, *args, **kwargs):
        super(AddStaticFileHashFlask, self).__init__(*args, **kwargs)
        self._file_hash_cache = {}

    def inject_url_defaults(self, endpoint, values):
        super(AddStaticFileHashFlask, self).inject_url_defaults(endpoint, values)
        if endpoint == "static" and "filename" in values:
            filepath = safe_join(self.static_folder, values["filename"])
            if os.path.isfile(filepath):
                cache = self._file_hash_cache.get(filepath)
                mtime = os.path.getmtime(filepath)
                if cache != None:
                    cached_mtime, cached_hash = cache
                    if cached_mtime == mtime:
                        values["h"] = cached_hash
                        return
                h = hashlib.md5()
                with contextlib.closing(open(filepath, "rb")) as f:
                    h.update(f.read())
                h = h.hexdigest()
                self._file_hash_cache[filepath] = (mtime, h)
                values["h"] = h


app = AddStaticFileHashFlask(__name__)

minify(app=app, html=True, js=True, cssless=True, static=True)
app.config.from_object(Config)


css_map = {"static/css/theme.css": "static/css/theme.min.css"}


def minify_css(css_map):
    for source, dest in css_map.items():
        with open(source, "r") as infile:
            with open(dest, "w") as outfile:
                outfile.write(rcssmin.cssmin(infile.read()))


mongo = PyMongo(app)
Session(app)

################Token Decorator#########################

SECRET_KEY = app.config['SECRET_KEY']
app.secret_key = SECRET_KEY


def token_required(something):
    @wraps(something)
    def wrap_token(*args, **kwargs):
        if 'logged_in' in session.keys():
            if session['logged_in']:
                return something(session['logged_in_id'], *args, **kwargs)
        try:
            token_passed = request.headers['TOKEN']
            if request.headers['TOKEN'] != '' and request.headers['TOKEN'] != None:
                try:
                    data = jwt.decode(token_passed, SECRET_KEY,
                                      algorithms=['HS256'])
                    return something(data['user_id'], *args, **kwargs)
                except jwt.exceptions.ExpiredSignatureError:
                    return_data = {
                        "error": "1",
                        "message": "Token has expired"
                    }
                    return jsonify(return_data)
            else:
                return_data = {
                    "error": "2",
                    "message": "Token required",
                }
                return jsonify(return_data)
        except Exception as e:
            print(e)
            return_data = {
                "error": "3",
                "message": "An error occured",
                "d_message": str(e)
            }
            return jsonify(return_data)
    return wrap_token
#########Require Login#################################################


def login_required(something):
    @wraps(something)
    def wrap_login(*args, **kwargs):
        if 'logged_in' in session and session["logged_in"]:
            return something(session['logged_in_id'], *args, **kwargs)
        else:
            flash("Please Sign In First")
            return redirect('/')
    return wrap_login

#########Scan representation############################################


def create_rep(r, user):
    reps = {
        "url":      '/static/images/scans/'+r['filename'],
        "scandate": timeago.format(r['scandate'], datetime.utcnow()),
        "position": r['position'],
        "city":     r['city'],
        "state":    r['state'],
        "id":       str(r['_id']),
        "upvote":   r['upvote'],
        "title":    r['title'],
        "urgency":  r["urgency"],
        "post_username": db.users.find_one({"_id": bson.ObjectId(r['u_id'])})['username'],
        "scan_list": str(db.users.find_one({"_id": bson.ObjectId(user)})['vote_scans'])
    }

    if r["des"]:
        reps["description"] = r["des"]
    return reps

########################################################################
#########################Forms##########################################
########################################################################


class LoginForm(FlaskForm):
    username = StringField("Username :", validators=[DataRequired()])
    password = PasswordField("Password :", validators=[DataRequired()])
    submit = SubmitField("Log In")


class SignupForm(FlaskForm):
    username = StringField("Username :", validators=[DataRequired()])
    password = PasswordField("Password :", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password :", validators=[DataRequired()])
    city = StringField("City :")
    submit = SubmitField("Register")
########################################################################
#########################Routes#########################################
########################################################################


@app.route('/')
def about():
    return render_template('index.html')


@app.route('/error')
def error():
    abort(404)


@app.route('/upload')
@login_required
def upload(user_id):
    return render_template('upload.html')


@app.route('/forum')
@login_required
def forum(user_id):
    return render_template('forum.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    if request.method == 'POST':
        userEmail = request.get_json()['email']
        issueHeader = request.get_json()["issueHeader"]
        issueDescription = request.get_json()["issueDescription"]
        if userEmail != None and userEmail.strip() != "":
            if issueHeader != None and issueHeader.strip() != "":
                if issueDescription != None and issueDescription.strip() != "":
                    db.issues.insert_one(
                        {"email": userEmail, "header": issueHeader, "description": issueDescription})
                    return jsonify({"error": "0", "message": "Message sent to admin, we appreciate your continued patronage"})
                elif issueDescription == None or issueDescription.strip() == "":
                    return jsonify({"error": "1", "message": "Issue Description can't be empty"})
            elif issueHeader == None or issueHeader.strip() == "":
                return jsonify({"error": "1", "message": "Subject Line can't be empty"})
        elif userEmail == None or userEmail.strip() == "":
            return jsonify({"error": "1", "message": "Make sure you give a valid email"})
        return jsonify('/contact')


@app.route("/gallery")
@login_required
def gallery(user_id):
    return render_template('gallery.html')


@app.route('/main', methods=['GET', 'POST'])
@login_required
def main(user_id):
    users = db['users']
    user = users.find_one({'_id': bson.ObjectId(session['logged_in_id'])})
    if request.method == "POST":
        if request.form.get("changepass"):
            newpass = request.form.get("newpass")
            confirmpass = request.form.get("confirmpass")
            if newpass == confirmpass and newpass is not None:
                users.update_one({'_id': bson.ObjectId(session['logged_in_id'])}, {
                                 '$set': {'password': pbkdf2_sha256.hash(newpass)}})
                return jsonify({"error": "0", "message": "Password changed successfully"})
            else:
                return jsonify({"error": "1", "message": "Password doesn't match"})
        if request.form.get("deleteacc"):
            users.remove({'_id': bson.ObjectId(session['logged_in_id'])})
            return redirect("/logout")
    return render_template("main.html", user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    error = False
    if login_form.validate_on_submit():
        users = db['users']
        result = users.find_one({
            'username': login_form.username.data,
        })
        if result is not None and pbkdf2_sha256.verify(login_form.password.data, result['password_hash']):
            session['logged_in'] = True
            session['logged_in_id'] = str(result['_id'])
            return redirect('/main')
        else:
            error = True
    return render_template("login.html", login_form=login_form, error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    usererror = False
    notallowed = False
    passlength = False
    if signup_form.validate_on_submit():
        users = db['users']
        dt_now = datetime.now(tz=timezone.utc)
        user = {
            "username": signup_form.username.data,
            "password_hash": pbkdf2_sha256.hash(signup_form.password.data),
            "signup_date": dt_now,
            "vote_scans": [],
        }
        if users.find_one({"username": user["username"]}) is not None:
            usererror = True
        elif signup_form.password.data != signup_form.confirm_password.data:
            notallowed = True
        elif len(signup_form.password.data) < 6:
            passlength = True
        else:
            users.insert_one(user)
            session['logged_in'] = True
            session['logged_in_id'] = str(user['_id'])
            return redirect('/main')
    return render_template("signup.html", signup_form=signup_form, usererror=usererror, notallowed=notallowed, passlength=passlength)


@app.route('/logout')
@login_required
def logout(u_is):
    session['logged_in'] = False
    session['logged_in_id'] = ''
    return redirect('/')


@app.errorhandler(404)
def pagenotfound(errorcode):
    return render_template("error.html", errorCode=404, errorMsg="Page not found"), 404
########################################################################
#########################API############################################
########################################################################


@app.route('/api')
def api_index():
    # Very simple
    return_data = {
        'title': 'API test'
    }
    return jsonify(return_data)


@app.route('/api/auth/token', methods=['POST'])
def api_login():
    # Get details from post request
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    users = db['users']
    result = users.find_one({
        'username': username,
    })
    if result != None and pbkdf2_sha256.verify(password, result['password_hash']):
        # Generate exp time and token and return them
        timeLimit = datetime.utcnow() + timedelta(minutes=24*60)
        payload = {"user_id": str(result['_id']), "exp": timeLimit}
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return_data = {
            "error": "0",
            "message": "Successful",
            "token": token,
            "Elapse_time": f"{timeLimit}",
        }
        return jsonify(return_data)
    # IF not correct credentials, give error reponse
    return_data = {
        "error": "1",
        "message": "Invalid username or password"
    }
    return jsonify(return_data)


@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    # Get details from post request
    username = request.get_json().get('username')
    # email = request.get_json().get('email')
    password = request.get_json().get('password')
    users = db['users']
    dt_now1 = datetime.utcnow()
    if users.find_one({"username": username}) is not None:
        return {"error": "1", "message": "Username already exists", "cause": "u"}
    users.insert_one({
        "username": username,
        "password_hash": pbkdf2_sha256.hash(password),
        "signup_date": dt_now1,
        "vote_scans": [],
    })
    return_data = {
        "error": "0",
        "message": "Successful",
    }
    return jsonify(return_data)


@app.route('/api/scans', methods=["GET", "POST"])
@token_required
def api_find(userId):
    scans = db['scans']
    position = request.get_json().get('position', [None, None])
    lat = position[0] if position[0] else 0
    long = position[1] if position[1] else 0
    radius = float(request.get_json().get('range', None))
    scans.create_index([('loc', '2dsphere')])
    result = []
    search = [
        {
            '$geoNear': {
                'near': [long, lat],
                'distanceField': 'dist',
                'spherical': True,
            }
        },
        {
            '$match': {
                'u_id': userId,
            },
        },
        {
            '$sort': {
                'dist': 1,
            }
        }
    ]
    if radius:
        search[0]['$geoNear']['maxDistance'] = radius
    elif not position[0]:
        search = [search[1], {
            '$sort': {
                'vote': -1,
            }
        }]
    result = scans.aggregate(search)
    repairs = []
    for r in result:
        scan = create_rep(r, session['logged_in_id'])
        repairs.append(scan)
    return {
        "repairs": repairs,
    }


@app.route('/api/scans/all', methods=["POST"])
@token_required
def api_find_all(userId):
    scans = db['scans']
    position = request.get_json().get('position', [None, None])
    lat = position[0] if position[0] else 0
    long = position[1] if position[1] else 0
    radius = float(request.get_json().get('range', None))
    scans.create_index([('loc', '2dsphere')])
    result = []
    search = [
        {
            '$geoNear': {
                'near': [long, lat],
                'distanceField': 'dist',
                'spherical': True,
            }
        },
        {
            '$sort': {
                'dist': 1,
            }
        }
    ]
    if radius:
        search[0]['$geoNear']['maxDistance'] = radius
    elif not position[0]:
        search = [{
            '$sort': {
                'vote': -1,
            }
        }]
    result = scans.aggregate(search)
    repairs = []
    for r in result:
        scan = create_rep(r, session['logged_in_id'])
        repairs.append(scan)
    return {
        "repairs": repairs,
    }


@app.route('/api/vote/voting', methods=["POST"])
@token_required
def api_upvote(userId):
    id_scan = bson.ObjectId(request.get_json().get('scan_id'))
    user = db.users.find_one({'_id': bson.ObjectId(userId)})
    scan = db.scans.find_one({'_id': bson.ObjectId(id_scan)})
    user_list = scan["vote_users"]
    scan_list = user["vote_scans"]
    user_name = str(user["_id"])
    userStatus = user_name in user_list
    if userStatus:
        user_list.remove(user_name)
        scan_list.remove(id_scan)
        db.scans.update_one({'_id': bson.ObjectId(id_scan)}, {
                            '$inc': {'upvote': -1}, '$set': {'vote_users': user_list}})
    else:
        user_list.append(user_name)
        scan_list.append(id_scan)
        db.scans.update_one({'_id': bson.ObjectId(id_scan)}, {
                            '$inc': {'upvote': 1}, '$set': {'vote_users': user_list}})
    db.users.update_one({'_id': user["_id"]}, {
                        '$set': {'vote_scans': scan_list}})
    return {
        "error": "0",
        "message": "Successful",
    }


@app.route('/api/vote/voted', methods=["POST"])
@token_required
def api_voted(userId):
    user = db.users.find_one({'_id': bson.ObjectId(userId)})
    id_scan = bson.ObjectId(request.get_json().get("scan_id"))
    scan = db.scans.find_one({'_id': id_scan})
    user_list = scan["vote_users"]
    scan_list = user["vote_scans"]
    user_name = str(user["_id"])
    if user_name in user_list:
        return {
            "error": "0",
            "voted": True
        }
    return {
        "error": "0",
        "voted": False
    }


@app.route('/api/scans/forum', methods=["POST"])
def api_find_forum():
    scans = db['scans']
    result = scans.find({}).sort([('upvote', pymongo.DESCENDING)])
    repairs = []
    for r in result:
        scan = create_rep(r, session['logged_in_id'])
        repairs.append(scan)
    return {
        "repairs": repairs,
    }


@app.route('/api/scans/gallery', methods=["POST"])
@token_required
def api_find_gallery(userId):
    scans = db['scans']
    result = scans.find({
        'u_id': userId
    }).sort([('upvote', pymongo.DESCENDING)])
    repairs = []
    for r in result:
        scan = create_rep(r, session['logged_in_id'])
        repairs.append(scan)
    return {
        "repairs": repairs,
    }


@app.route('/api/scans/upload', methods=["POST"])
@token_required
def api_upload(userId):
    f = request.files['image']
    # for now it is saving as a jpeg but that will be changed
    filename = secure_filename(str(uuid4())+".jpeg")
    f.save(os.path.join('static/images/scans/', filename))
    return {"error": "0", "filename": filename, }


@app.route('/api/scans/add', methods=["POST"])
@token_required
def api_add(userId):
    scans = db['scans']
    position = request.get_json().get('position')

    lat = int(position[0])
    long = int(position[1])
    address = Nominatim(user_agent="georepair").reverse(
        [lat, long]).raw['address']
    city = None
    if 'city' in address:
        city = address.get('city')
    elif 'town' in address:
        city = address.get('town')
    elif 'village' in address:
        city = address.get('village')
    state = address.get('state')
    filename = request.get_json().get('filename')
    title = request.get_json().get('title')
    des = request.get_json().get('des', None)
    urgency = request.get_json().get('urgency', 0)
    dt_now = datetime.utcnow()
    scans.insert_one({
        "u_id": userId,
        "filename": filename,
        "scandate": dt_now,
        "position": {
            "lat": lat,
            "long": long
        },
        "loc": {
            "type": "Point",
            "coordinates": [long, lat]
        },
        "upvote": 0,
        "title": title,
        "des": des,
        "urgency": urgency,
        "vote_users": [],
        "city": city,
        "state": state
    })
    return {"error": "0", "message": "Succesful", }


@app.route('/api/wel', methods=['POST'])
@token_required
def api_welcome(userId):
    users = db['users']
    user = users.find_one({'_id': bson.ObjectId(userId)})
    # Code explains itself (note the new paraameter from the decorator)
    return_data = {
        "error": "0",
        "user": {
            "username": user['username']
        },
        "message": "You Are verified"
    }
    return jsonify(return_data)


if __name__ == "__main__":
    minify_css(css_map)
    app.run(debug=True)
