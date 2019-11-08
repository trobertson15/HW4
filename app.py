from flask import Flask
from flask import render_template, redirect, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
#import secrets
import os

dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbname = os.environ.get('DBNAME')

#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser, dbpass, dbhost, dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

class trobrtson_myheroacademiaapp(db.Model):
    heroId = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    quirk = db.Column(db.String(255))

    def __repr__(self):
        return "id: {0} | first name: {1} | last name: {2} | quirk: {3}".format(self.heroId, self.first_name, self.last_name, self.quirk)

class HeroForm(FlaskForm):
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    quirk = StringField('Quirk:', validators=[DataRequired()])


@app.route('/')
def index():
    all_heroes = trobrtson_myheroacademiaapp.query.all()
    return render_template('index.html', heroes=all_heroes, pageTitle='My Hero Academia Heroes')

@app.route('/add_hero', methods=['GET', 'POST'])
def add_hero():
    form = HeroForm()
    if form.validate_on_submit():
        hero = trobrtson_myheroacademiaapp(first_name=form.first_name.data, last_name=form.last_name.data, quirk=form.quirk.data)
        db.session.add(hero)
        db.session.commit()
        flash('Hero was successfully added!')
        return redirect('/')

    return render_template('add_hero.html', form=form, pageTitle='Add A New Hero')

@app.route('/delete_hero/<int:heroId>', methods=['GET','POST'])
def delete_hero(heroId):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        obj = trobrtson_myheroacademiaapp.query.filter_by(heroId=heroId).first()
        db.session.delete(obj)
        db.session.commit()
        flash('Hero was successfully deleted!')
        return redirect("/")

    else: #if it's a GET request, send them to the home page
        return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
