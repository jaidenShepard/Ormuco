import os

from flask import Flask, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy

from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisprobablyisntasafestring'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

# Routes
@app.route('/', methods=['get', 'post'])
def index():
    form = SurveyForm()
    alert_type = 'success'
    if form.validate_on_submit():
        entry = Survey.query.filter_by(name=form.name.data).first()

        if entry is not None:
            flash("Someone with that name has already made a submission!")
            return conflict(form.errors)

        entry = Survey(
                name=form.name.data,
                color=form.color.data,
                pet=form.pet.data
                )
        db.session.add(entry)
        db.session.commit()

        form.name.data = ''
        form.color.data = ''
        form.pet.data = ''

        flash("Thanks for your submission!")
        return redirect(url_for('index'))

    return render_template('index.html', form=form, alert_type=alert_type)

# Database Models
class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    color = db.Column(db.String(20))
    pet = db.Column(db.String(4))

    def __init__(self, name, color, pet):
        self.name = name
        self.color = color
        self.pet = pet

    def __repr__(self):
        return '<Name %r>' % self.name

db.create_all()
db.session.commit()

# Forms
class SurveyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    color = StringField('Favorite Color', validators=[DataRequired()])
    pet = RadioField(
        'Cats or Dogs?',
        choices=[('cat', 'cat'), ('dog', 'dog')],
        validators=[DataRequired()]
        )
    submit = SubmitField('Submit')


#Error Handlers
@app.errorhandler(409)
def conflict(e):
    form = SurveyForm()
    return render_template('index.html', form=form, alert_type='danger'), 409

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run()
