import flask
from flask import Flask,flash,redirect,render_template, request, session, url_for, jsonify
from flask_cors import CORS
import numpy as np
import pickle

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

 

import sqlite3
import requests

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "Iz76NcBoPcq5gVF5Qby8Ltj7p-E4igMYeaNXaG3gFlTK"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

app=Flask(__name__)
app.secret_key="#@universityflaskapp@#"

# database creation
con=sqlite3.connect("database.db")
print("Opened database successfully")
con.execute("create table if not exists customer(pid integer primary key, name text, email text, password text,status BOOLEAN)")
print("Table created successfully")
con.close()

@app.route("/",methods=['POST','GET'])
def index():
    return render_template('login.html')

# @app.route("/register",methods=['POST','GET'])
# def register():
#     return render_template('register.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/form1",methods=['POST','GET'])
def form1():
    return render_template('form1.html')



@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')




@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            name=request.form['name']
            email=request.form['email']
            password=request.form['password']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("INSERT INTO customer(name,email,password) VALUES (?,?,?)",(name,email,password))
            con.commit()
            flash("Registered successfully","success")
        except:
            con.rollback()  
            flash("Problem in Registration, Please try again","danger")
        finally:
            return render_template("login.html")
            con.close()
    else:
        return render_template('register.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("SELECT * FROM customer where email=? and password=?",(email,password))
        data=cur.fetchone()

        if data:
            session["email"]=data["email"]
            print("sent to home")
            return redirect(url_for("home"))
                      
        else:
            flash("Username or Password is incorrect","danger")
            print("not sent to home")
            return redirect(url_for("login"))


@app.route("/predict1",methods = ['POST'])
def predict1():

    month = request.form.get("month")
    date =  request.form.get("date")
    
    Flight_No = request.form.get("Flight_No")
    origin_airport_id = request.form.get("origin_airport_id")
    dest_airport_id = request.form.get ("dest_airport_id")
    crs_dep_time = request.form.get("crs_dep_time")
    crs_arr_time = request.form.get("crs_arr_time")
    dep_time = request.form.get("dep_time")

    model = pickle.load(open("flight.pkl","rb"))

    feature = np.array([[month, date, Flight_No, origin_airport_id, dest_airport_id, crs_dep_time,crs_arr_time, dep_time]])

    # NOTE: manually define and pass the array(s) of values to be scored in the next line
    payload_scoring = {"input_data": [{"fields": [['month', 'date', 'Flight_No', 'origin_airport_id', 'dest_airport_id', 'crs_dep_time','crs_arr_time', 'dep_time']], "values":'feature'}]}

    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/c6bb7dc9-da68-4a21-a9f0-93355cc2208e/predictions?version=2022-11-20', json=payload_scoring,
    headers={'Authorization': 'Bearer ' + mltoken})
    print(response_scoring)
    #print(response_scoring.json())
    prediction=response_scoring.json()
    predict=prediction['prediction'][0]['values'][0][0]
    print("Final prediction:",predict)

    if predict[0]== 1:
        print(predict[0])
        return render_template('failed1.html',predict=predict[0])
    else:
        return render_template('success1.html',predict=predict[0])


   


if __name__ =='__main__':
    app.run(Debug=True)