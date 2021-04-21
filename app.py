from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from flask_mysqldb import MySQL
import pygeoip, json
import re
import json, requests
from requests import get
import MySQLdb
import mysql.connector
import MySQLdb.cursors
from geopy.geocoders import Nominatim
from flask_simple_geoip import SimpleGeoIP




app = Flask(__name__)
app.secret_key = 'password1'


#mysql =  MySQL(app)

 #Setting up database connection
#db = mysql.connector.connect(
 #   host = "localhost",
  #  user = "root",
   # password="password1",
    #database = "guidedatabase")
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password1'
app.config['MYSQL_DB'] = 'projectdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config["GEOIPIFY_API_KEY"] = "at_xVYxEOVei1KehHkjpqkFoWPJBXJW9"


#Initialise SQL 
mysql = MySQL(app)
API_KEY = 'AIzaSyB9uGV437zMV4Ne7yM3a3twM7CUALUcm2g'
GEOIPIFY_API_KEY = 'at_MuzI8z9iadoOwbkfh5Jx12hw9wgZK'
simple_geoip = SimpleGeoIP(app)




#8cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)



#Creating table User
#cursor.execute("CREATE TABLE IF NOT EXISTS Users (userID int PRIMARY KEY AUTO_INCREMENT, user_name VARCHAR(50) NULL, user_username VARCHAR(45), user_password VARCHAR(30), age smallint UNSIGNED, user_emailadress VARCHAR(50)  )")
#cursor.execute("CREATE TABLE IF NOT EXISTS Venue(placeID VARCHAR(50) PRIMARY KEY, place_name VARCHAR(50) NULL, place_city VARCHAR(40))")
#cursor.execute("CREATE TABLE IF NOT EXISTS Favourites (userID int, placeID VARCHAR(50),FOREIGN KEY(userID) REFERENCES User(userID),FOREIGN KEY(placeID) REFERENCES Venue(placeID))")


#Commiting a new user  to the database


@app.route("/")
def main():

    return render_template('home.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    #message to be displayed if error occurs 
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        user_account = cursor.fetchone()
        # If account exists in accounts table in out database
        if user_account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session["id"] = user_account["id"]
            session["username"] = user_account["username"]
            # Redirect to home page
            return redirect(url_for('main'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    #Redirecting to home page
    return redirect(url_for('main'))

@app.route('/login/register', methods = ['GET', 'POST'])
def register():
    #error message to user
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        #Create variables
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_account = cursor.fetchone()
        # If account exists show error and validation checks
        if user_account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users VALUES (NULL, %s, %s, %s)", (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('main'))
    elif request.method ==  'POST':   
        msg = 'Please fill out the form to continue'
    #show registration form and error message if error occured 
    return render_template('register.html', msg = msg )     

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        user_account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', user_account = user_account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/currentlocation", methods = ['GET','POST'])
def get_current_location():
    url = "http://ip-api.com/json/"
    res = requests.get(url)
    data = json.loads(res.content)
    lat = data['lat']
    lon = data['lon']
    city = data['city']
    

    return render_template("home.html", data = city)


    
@app.route('/venues', methods = ['GET','POST'])
def search_venues():
    msg = ''
    if request.method == 'POST':
        address = request.form['addr']
        
        geolocator = Nominatim(user_agent="foursquare_agent")

        #converting address to longitude and latitude
        location = geolocator.geocode(address)
        lat = location.latitude
        lon = location.longitude

    print(lat,lon)

    global search_criteria 
    search_criteria= request.form['act']

    
    url  =   "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius=1500&type={}&key={}".format(
    lat,
    lon,
    search_criteria,
    API_KEY)
        
    res = requests.get(url)
    data = json.loads(res.content)

    i = 0
    get_image = []

    try:
        get_image = get_image.append(data["photo_reference"])
    except KeyError:
        get_image = get_image.append('/static/images/beach.jpg')


    
    if data.get('status') == 'ZERO_RESULTS':
        msg = "Sorry, we have no results for your search. Try again!"
    
    else:
        msg = 'Here are the results for ' + search_criteria +'s in ' +address

    return render_template('venues.html', 
        data = data['results'],
        msg=msg)


def get_images(data):
    
    i = 0
    get_image = []

    for i in data:
        try:
            get_image = get_image.append(data["results"]["photos"]["photo_reference"])
        except KeyError:
            get_image = get_image.append('/static/images/beach.jpg')
        i= i+1
    return get_image

@app.route('/venues/<string:id>', methods = ['GET','POST'])
def get_venue(id):
    venue_id=id
    venue_fields ='place_id,name,formatted_address,name,type,photo,formatted_phone_number,international_phone_number,opening_hours,website,price_level,rating,review'
    url = "https://maps.googleapis.com/maps/api/place/details/json?place_id={}&fields={}&key={}".format(
        venue_id,
        venue_fields,
        API_KEY
    )

    response = requests.get(url)
    data = json.loads(response.content)
    #print(data)


    return view_venue(data)

def view_venue(data):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if data != "":
        get_id = data ["result"]["place_id"]
        try:
            get_website = data["result"]["website"]
        except KeyError :
            get_website=""
        except KeyError:
            get_wesbite = "No website info available"
        try:
            get_name = data['result']['name']
        except KeyError:
            get_name = ""

        try:
            get_address = data['result']['formatted_address']
        except KeyError:
            get_address = ""

        try:
            get_phone_number = data['result']['international_phone_number']
        except KeyError:
            get_phone_number = "No phone number available"

        #try:
        #    get_reviews = data['result']['reviews']
        #except KeyError:
        #    get_reviews = []

        try:
            photos = data['result']['photos']
            photo_ref_list =[]
            i = 0
            for photo in photos:
                get_photos = data['result']['photos'][i]['photo_reference']
                photo_ref_list.append(get_photos)
                i = i+1
        except KeyError:
            get_photos =[]

        try: 
            reviews = get_venue_reviews(get_id)
            reviews_list =[]
            for review in reviews:
                reviews_list.append(review)
        except KeyError:
            reviews_list=[]
        
        print(reviews_list)


        print(photo_ref_list)

        cursor.execute("SELECT * FROM venues WHERE id = %s", (get_id,))
        venue_row = cursor.fetchone()
        # If venue already exists insert favourite
        if venue_row == None:
            cursor.execute("INSERT INTO venues (id,city,name) VALUES(%s,%s,%s)",(get_id,get_address,get_name))
            mysql.connection.commit()
            print("VENUE ADDED ")
        

        
        return render_template('venue.html',
            place_id = get_id,
            website = get_website,
            name = get_name,
            address = get_address,
            phone_number = get_phone_number,
            reviews = reviews_list,
            photos = photo_ref_list)

    else:
        return render_template('home.html')


    
@app.route('/venue/<string:id>/', methods = ['GET','POST'])
def add_favourite(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # insert user id and place id into favourites table
    get_userID = (session['id'])
    get_placeID = id
    
    cursor.execute("SELECT * from favourites WHERE venueID = %s",(get_placeID,))
    fav_row = cursor.fetchone()
    # If venue already exists insert favourite
    if fav_row == None:
        cursor.execute("INSERT INTO favourites (favID,userID,venueID) VALUES (NULL,%s,%s)",(get_userID,get_placeID))
        mysql.connection.commit()
        msg = 'Favourite Added'

    else:
        msg = "Favourite already added"
    
    mysql.connection.commit()
    return  get_favourites()



@app.route('/favourites', methods = ['GET','POST'])
def get_favourites():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from favourites ")
    check_favs = cursor.fetchall()
    if check_favs == None:
        msg = "You do not have any favourites yet"
    else:
        get_user = (session['id'])
        cursor.execute("SELECT venueID from favourites WHERE userID = %s ",(get_user,))
        user_favourites = cursor.fetchall()
        venue_fields ='place_id,name,formatted_address,name,type,photo'
        results = []

        i = 0


        while i < len(user_favourites):
            url = "https://maps.googleapis.com/maps/api/place/details/json?place_id={}&fields={}&key={}".format(
            user_favourites[i].get("venueID"),
            venue_fields,
            API_KEY
        )   
            
            res = requests.get(url)
            data = json.loads(res.content) 
            results.append(data)
            i=i+1

    
    return render_template('favourites.html' , data = results)
    


@app.route('/favourites/<string:id>', methods = ['GET','DELETE'])
def delete_favourite(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    venueID = id
    print(venueID)
    cursor.execute("DELETE FROM favourites WHERE venueID = %s",(venueID,))
    mysql.connection.commit()
    msg = "Favourite Removed"

    return redirect(url_for('get_favourites'))


@app.route('/favourites/', methods =['GET','POST'])
def filter_favourite():
    msg = ''
    i = 0
    venue_fields ='place_id,name,formatted_address,name,type,photo'
    result = []
    

    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        get_userID = (session['id'])
        filter_query = request.form['filter']


        sql = "SELECT venues.id     FROM venues     INNER JOIN favourites   ON favourites.venueID=venues.id     WHERE favourites.userID = 2  AND  venues.city LIKE %s"

        like_value = f'%{filter_query}%'

        cursor.execute(sql,(like_value,))
        user_favs = cursor.fetchall()


        while i < len(user_favs):
            url = "https://maps.googleapis.com/maps/api/place/details/json?place_id={}&fields={}&key={}".format(
            user_favs[i].get("id"),
            venue_fields,
            API_KEY
        )   
            print(url)
            res = requests.get(url)
            data = json.loads(res.content) 
            result.append(data)
            i=i+1

        msg = 'User Favourites'
    else:
        msg = 'Not Found'

    return render_template('favourites.html', data=result)


@app.route("/venues/<string:id>/", methods = ['GET','POST'])
def add_review(id):
    msg = ''
    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        get_userID = (session['id'])
        user_fullname = request.form['name']
        user_review = request.form['review']
        venueID = id

        cursor.execute("INSERT INTO reviews VALUES (NULL,%s,%s,%s,%s)",(get_userID,venueID,user_review,user_fullname))
        mysql.connection.commit()

        msg = "Review Added"

    elif not user_fullname or not user_review :
        msg = 'Please fill out the form!'
    
    else:
        msg = 'Please fill out the form!'

    return get_venue(venueID)

@app.route("/venues/<string:id>/reviews", methods = ['GET','POST'])
def get_venue_reviews(id):
    msg = ''
    venueID = id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from reviews WHERE venueID = %s",(venueID,))
    reviews = cursor.fetchall()
    if reviews == None:
        msg = "There are no reviews for this venue yet"
    
        
    return reviews

@app.route("/venues/<string:id>/reviews", methods = ['DELETE'])
def delete_venue_reviews(v_id, r_id):
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    reviewID = r_id
    venueID = v_id

    cursor.execute("DELETE FROM reviews WHERE id = %s",(reviewID,))

    return get_venue(venueID) 






if __name__ == "__main__":
    app.debug = True
    app.run()
    
   # https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJofA33u8iYUgRw5sYaIvyoOk&key=AIzaSyAvi7VtnLjgF1ezfFdBijVEV_l0upGSJB0&key=AIzaSyAvi7VtnLjgF1ezfFdBijVEV_l0upGSJB0