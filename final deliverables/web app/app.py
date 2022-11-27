from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify

import numpy as np
import pickle

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

 

import sqlite3

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
   
    print(feature)

    prediction = model.predict(feature)

    print(prediction)

    if prediction[0]== 1:
        print(prediction[0])
        return render_template('failed1.html',prediction=prediction[0])
    else:
         return render_template('success1.html',prediction=prediction[0])


   


if __name__ =='__main__':
    app.run(Debug=True)