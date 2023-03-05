from flask import Flask, jsonify, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired,input_required,optional
from flask_sqlalchemy import SQLAlchemy
from random import choice
import os

# file_path = os.path.abspath(os.getcwd())+"\cafe.db"
# print(file_path)
file_path='E://Cafe_API//cafes.db'

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_SILENCE_UBER_WARNING']=1
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


def to_dict(self):
    return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")



## HTTP GET - Read Record

@app.route('/random')
def random():
    # id=randint(1,)
    cafes = db.session.query(Cafe).all()
    random_cafe = choice(cafes)
    print(random_cafe)
    return jsonify(cafe=to_dict(random_cafe))


@app.route("/all")
def all():
    all_cafes = db.session.query(Cafe).all()
    cafes = [to_dict(cafe) for cafe in all_cafes]
    return jsonify(cafes=cafes)


@app.route('/search')
def search():
    loc = request.args.get('loc')  # taking the loc arguement
    results = db.session.query(Cafe).filter(Cafe.location == loc).all()
    cafes = [to_dict(cafe) for cafe in results]
    print(cafes)
    if cafes == []:
        mssg = {'Not Found': "Sorry, we don't have a cafe at that location"}
        return jsonify(error=mssg)
    return jsonify(cafes=cafes)


## HTTP POST - Create Record

@app.route('/add',methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )

    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>",methods=['PATCH'])
def update_price(cafe_id):
    new_price=request.args.get('new_price')
    cafe_to_update=Cafe.query.get(cafe_id)
    if cafe_to_update==None:
        return jsonify(error={'Not found':'Sorry a cafe with that id was not found in the database'}),404
    cafe_to_update.coffee_price=new_price
    db.session.commit()
    return jsonify({'success':'Successfully updated the price'}),200




## HTTP DELETE - Delete Record

API_KEY='TopSecretAPIKey'

@app.route("/report-close/<cafe_id>",methods=['DELETE'])
def delete_cafe(cafe_id):
    cafe_to_delete=Cafe.query.get(cafe_id)

    api_key=request.args.get('api-key')
    if api_key!=API_KEY:
        return jsonify({'error':"Sorry, that's not allowed. Make sure you have the correct api_key"}),403
    if cafe_to_delete==None:
        return jsonify(error={'Not found':'Sorry a cafe with that id was not found in the database'}),404
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return jsonify({'success':'Successfully updated the price'}),200




if __name__ == '__main__':
    app.run(debug=True)
