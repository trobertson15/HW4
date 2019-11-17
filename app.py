from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
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
    role = db.Column(db.String(255))
    occupation = db.Column(db.String(255))

    def __repr__(self):
        return "id: {0} | first name: {1} | last name: {2} | quirk: {3} | role: {4} | occupation: {5}".format(self.heroId, self.first_name, self.last_name, self.quirk, self.role, self.occupation)

class MHAForm(FlaskForm):
    heroId = IntegerField('Hero ID:')
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    quirk = StringField('Quirk:', validators=[DataRequired()])
    role = StringField('Role:', validators=[DataRequired()])
    occupation = StringField('Occupation:', validators=[DataRequired()])

@app.route('/')
def index():
    all_characters = trobrtson_myheroacademiaapp.query.all()
    return render_template('index.html', characters=all_characters, pageTitle='My Hero Academia Heroes and Villains')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['search_string']
        search = "%{0}%".format(search_value)
        results = trobrtson_myheroacademiaapp.query.filter(or_(trobrtson_myheroacademiaapp.first_name.like(search), trobrtson_myheroacademiaapp.last_name.like(search), trobrtson_myheroacademiaapp.quirk.like(search), trobrtson_myheroacademiaapp.role.like(search), trobrtson_myheroacademiaapp.occupation.like(search))).all()
        return render_template('index.html', characters=results, pageTitle='My Hero Academia: Heroes and Villains', legend="Search Results")

@app.route('/add_character', methods=['GET', 'POST'])
def add_character():
    form = MHAForm()
    if form.validate_on_submit():
        character = trobrtson_myheroacademiaapp(first_name=form.first_name.data, last_name=form.last_name.data, quirk=form.quirk.data, role=form.role.data, occupation=form.occupation.data)
        db.session.add(character)
        db.session.commit()
        flash('New character was successfully added!')
        return redirect('/')

    return render_template('add_character.html', form=form, pageTitle='Add A New Hero Or Villain')

@app.route('/delete_character/<int:heroId>', methods=['GET','POST'])
def delete_character(heroId):
    if request.method == 'POST': #if it's a POST request, delete the character from the database
        obj = trobrtson_myheroacademiaapp.query.filter_by(heroId=heroId).first()
        db.session.delete(obj)
        db.session.commit()
        flash('Character was successfully deleted!')
        return redirect("/")
    else: #if it's a GET request, send them to the home page
        return redirect("/")

@app.route('/character/<int:heroId>', methods=['GET','POST'])
def character(heroId):
    character = trobrtson_myheroacademiaapp.query.get_or_404(heroId)
    return render_template('character.html', form=character, pageTitle='Character Details')

@app.route('/character/<int:heroId>/update', methods=['GET','POST'])
def update_character(heroId):
    character = trobrtson_myheroacademiaapp.query.get_or_404(heroId)
    form = MHAForm()
    if form.validate_on_submit():
        character.first_name = form.first_name.data
        character.last_name = form.last_name.data
        character.quirk = form.quirk.data
        character.role = form.role.data
        character.occupation = form.occupation.data
        db.session.commit()

        flash('This character has been updated!')
        return redirect(url_for('character', heroId=character.heroId))
    #elif request.method == 'GET':
    form.first_name.data = character.first_name
    form.last_name.data = character.last_name
    form.quirk.data = character.quirk
    form.role.data = character.role
    form.occupation.data = character.occupation

    return render_template('update_character.html', form=form, pageTitle='Update Heroes And Villains',
                            legend="Update A Hero Or Villain")

if __name__ == '__main__':
    app.run(debug=True)
