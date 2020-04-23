from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
from environs import Env
import os


app = Flask(__name__)
CORS(app)
heroku = Heroku(app)

env = Env()
env.read_env()
DATABASE_URL = env("DATABASE_URL")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
# app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL


db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    inventory = db.relationship('Vehicle')

    def __init__(self, name, email):
        self.name = name
        self.email = email

class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.Integer)
    make = db.Column(db.String)
    model = db.Column(db.String)
    purchase_price = db.Column(db.Integer)
    list_price = db.Column(db.Integer)
    sale_price = db.Column(db.Integer)
    miles = db.Column(db.Integer)
    purchase_location = db.Column(db.String)
    purchase_date = db.Column(db.DATE)
    sold_date = db.Column(db.DATE)
    sold = db.Column(db.Bool)
    repairs = db.relationship('Repair')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="vehicles")

    def __init__(self, year, make, model, purchase_price, list_price, sale_price, miles, purchase_location, purchase_date, sold_date, sold, user_id):
        self.year = year
        self.make = make
        self.model = model
        self.purchase_price = purchase_price
        self.list_price = list_price
        self.sale_price = sale_price
        self.miles = miles
        self.purchase_location = purchase_location
        self.purchase_date = purchase_date
        self.sold_date = sold_date
        self.sold = sold
        self.user_id = user_id


class Repair(db.Model):
    __tablename__ = "repairs"
    id = db.Column(db.Integer, primary_key = True)
    shop = db.Column(db.String)
    work_description = db.Column(db.String)
    parts_cost = db.Column(db.Integer)
    labor_cost = db.Column(db.Integer)
    labor_hours = db.Column(db.Integer)
    date = db.Column(db.DATE)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    vehicle = db.relationship("Vehicle", back_populates="repairs")

    def __init__(self, shop, work_description, parts_cost, labor_cost, labor_hours, date, vehicle_id):
        self.shop = shop
        self.work_description = work_description
        self.parts_cost = parts_cost
        self.labor_cost = labor_cost
        self.labor_hours = labor_hours
        self.date = date
        self.location = location
        self.vehicle_id = vehicle_id

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email")

class VehicleSchema(ma.Schema):
    class Meta:
        fields = ("id", "year", "make", "model", "purchase_price", "list_price", "sale_price", "miles", "purchase_location", "purchase_date", "sold_date", "sold", "user_id")

class RepairSchema(ma.Schema):
    class Meta:
        fields = ("id", "shop", "work_description", "parts_cost", "labor_cost", "labor_hours", "date", "vehicle_id")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)

repair_schema = RepairSchema()
repairs_schema = RepairSchema(many=True)

# CRUD

# GET User
@app.route("/user/<email>", methods=["GET"])
def get_user(email):
    found_user = User.query.filter(User.email == email)
    # all_users = db.session.query(Alert).join(User).filter(User.id == Alert.user_id).all()
    userResult = user_schema.dump(found_user)

    if userResult:
        return jsonify(userResult)
    else:
        return jsonify("User not found")

# Get all users
@app.route("/users", methods=["GET"])
def get_users():
    all_users = User.query.all()
    usersResult = users_schema.dump(all_users)

    return jsonify(all_users)

# Get Vehicles by userID
@app.route("/vehicles/<id>", methods=["GET"])
def get_vehicles(id):
    user_vehicles = Vehicle.query.filter(Vehicle.user_id == id).all()
    vehicleResult = vehicles_schema.dump(user_vehicles)

    if vehicleResult:
        return jsonify(vehicleResult)
    else:
        return jsonify("No vehicles found")

# Get all Vehicles
@app.route("/vehicles", methods=["GET"])
def get_all_Vehicles():
    all_vehicles = Vehicle.query.all()
    inventoryResult = vehicles_schema.dump(all_vehicles)

    if inventoryResult:
        return jsonify(inventoryResult)
    else:
        return jsonify("no inventory")

#GET repairs by vehicle id
@app.route("/repairs/<id>", methods=["GET"])
def get_repairs(id):
    all_repairs = Repair.query.filter(Repair.vehicle_id == id).all()
    repairResult = repairs_schema.dump(all_repairs)

    return jsonify(repairResult)


# POST new user
@app.route("/user", methods=["POST"])
def add_user():
    name = request.json["name"]
    email = request.json["email"]

    new_user = User(name)

    db.session.add(new_user)
    db.session.commit()

    user = User.query.get(new_user.name)
    return user_schema.jsonify(user)


# POST new vehicle
@app.route("/vehicle", methods=["POST"])
def add_vehicle():
    year = request.json["year"]
    make = request.json["make"]
    model = request.json["model"]
    purchase_price = request.json["purchase_price"]
    list_price = request.json["list_price"]
    sale_price = request.json["sale_price"]
    miles = request.json["miles"]
    purchase_location = request.json["purchase_location"]
    purchase_date = request.json["purchase_date"]
    sold_date = request.json["sold_date"]
    sold = request.json["sold"]
    user_id = request.json["user_id"]

    new_vehicle = Vehicle(year, make, model, purchase_price, list_price, sale_price, miles, purchase_location, purchase_date, sold_date, sold, user_id)

    db.session.add(new_vehicle)
    db.session.commit()

    vehicle = Vehicle.query.get(new_vehicle.user_id)
    return vehicle_schema.jsonify(vehicle)

# POST new repair
@app.route("/repair", methods=["POST"])
def add_repair():
    shop = request.json["shop"]
    work_description = request.json["work_description"]
    parts_cost = request.json["parts_cost"]
    labor_cost = request.json["labor_cost"]
    labor_hours = request.json["labor_hours"]
    date = request.json["date"]
    vehicle_id = request.json["vehicle_id"]

    new_repair = Repair(shop, work_description, parts_cost, labor_cost, labor_hours, date, vehicle_id)

    db.session.add(new_repair)
    db.session.commit()

    repair = Repair.query.get(new_repair.vehicle_id)
    return repair_schema.jsonify(repair)

# PUT/PATCH by ID -- Not sure what we would patch at the moment, I can update this if I find a use
# @app.route("/alert/<id>", methods=["PATCH"])
# def delete_alert(id):
#     alert = Alert.query.get(id)

#     new_alert = request.json["alert"]

#     todo.done = new_car

#     db.session.commit()
#     return car.jsonify(alert)

# DELETE Vehicle
@app.route("/vehicle/<id>", methods=["DELETE"])
def delete_vehicle(id):
    vehicle = Vehicle.query.get(id)
    db.session.delete(vehicle)
    db.session.commit()

    return jsonify("Vehicle Deleted")

# DELETE Repair
@app.route("/repair/<id>", methods=["DELETE"])
def delet_repair(id):
    repair = Repair.query.get(id)
    db.session.delete(repair)
    db.session.commit()

    return jsonify("Repair Deleted and stuff")

# DELETE User
@app.route("/user/<id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return jsonify("User Deleted")

# TODO get vehicle or repairs by year, make, model, price range, purchase date, sale date, current inventory, etc


if __name__ == "__main__":
    app.debug = True
    app.run()