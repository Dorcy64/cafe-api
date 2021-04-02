from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

from sqlalchemy.orm.exc import UnmappedInstanceError

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record

@app.route("/random")
def random_cafe():
    rand_cafe = random.choice(db.session.query(Cafe).all())
    cafe_output = {
        "can_take_calls": rand_cafe.can_take_calls,
        "coffee_price": rand_cafe.coffee_price,
        "has_sockets": rand_cafe.has_sockets,
        "has_toilet": rand_cafe.has_toilet,
        "has_wifi": rand_cafe.has_wifi,
        "img_url": rand_cafe.img_url,
        "location": rand_cafe.location,
        "map_url": rand_cafe.map_url,
        "name": rand_cafe.name,
        "seats": rand_cafe.seats
    }

    return jsonify(cafe=cafe_output)


@app.route("/all")
def all_cafes():
    cafes_list = db.session.query(Cafe).all()
    output_cafe_list = []
    for cafe in cafes_list:
        cafes = {
            "caffe_id": cafe.id,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price,
            "has_sockets": cafe.has_sockets,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "map_url": cafe.map_url,
            "name": cafe.name,
            "seats": cafe.seats
        }
        output_cafe_list.append(cafes)

    return jsonify(cafes_list=output_cafe_list)


@app.route("/search", methods=["GET"])
def search_cafes():
    loc = request.args.get("loc")
    print(loc)
    if loc is not None:
        cafe_loc = Cafe.query.filter(Cafe.location == loc).first()
        print(cafe_loc)
        if cafe_loc is not None:
            cafes = {
                "caffe_id": cafe_loc.id,
                "can_take_calls": cafe_loc.can_take_calls,
                "coffee_price": cafe_loc.coffee_price,
                "has_sockets": cafe_loc.has_sockets,
                "has_toilet": cafe_loc.has_toilet,
                "has_wifi": cafe_loc.has_wifi,
                "img_url": cafe_loc.img_url,
                "location": cafe_loc.location,
                "map_url": cafe_loc.map_url,
                "name": cafe_loc.name,
                "seats": cafe_loc.seats
            }
            return jsonify(cafe=cafes)
        else:
            error = {
                "Not Found": "Sorry, we don't have a cafe at that location"
            }
            return jsonify(error=error), 404
    else:
        return jsonify({"error": {"Not Found": "Entry not recognised"}}), 404


## HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def add_coffee_shop():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.values.get("name"),
            map_url=request.values.get("map_url")
        )
        db.session.add(new_cafe)
        db.session.commit()
        response = {
            "success": "Successfully added the new cafe."
        }
        return jsonify(response=response)
    else:
        return jsonify({"error": {"Not Found": "Invalid Parameters"}})


## HTTP PUT/PATCH - Update Record

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_update_price(cafe_id):
    if cafe_id:
        new_price_input = request.values.get("new_price")
        if new_price_input is not None:
            to_edit = Cafe.query.get(cafe_id)
            to_edit.coffee_price = new_price_input
            db.session.commit()
            return jsonify({"Success": "Successfully updated the price"})
        else:
            return jsonify({"Invalid Parameter": "Sorry the parameter was not found"}), 404
    else:
        return jsonify({"error": {"Not Found": "Sorry a cafe with  that id was not found in the database"}}), 404


## HTTP DELETE - Delete Record

@app.route("/report-closed/<int:key_id>", methods=["DELETE"])
def report_closed(key_id):
    api_key = request.values.get("api_key")
    if api_key == "TopSecretAPIKey" and api_key is not None:
        if key_id:
            try:
                to_be_deleted = Cafe.query.get(key_id)
                db.session.delete(to_be_deleted)
                db.session.commit()
                return jsonify({"success": "Successfully deleted"})
            except UnmappedInstanceError:
                return jsonify({"error": {"Not Found": "Sorry a cafe with that id was not found in the database"}})
        else:
            return jsonify({"error": {"Not Found": "The id was not found"}}), 404
    else:
        return jsonify({"error":
            {
                "Not Allowed": "Sorry, that's not allowed. Make sure you have the correct api_key"
            }
        }), 403


if __name__ == '__main__':
    app.run(debug=True)
