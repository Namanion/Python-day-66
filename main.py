import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask import jsonify

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        #Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            print(column)
            # print(column.name)
            # print(getattr(self, column.name))
            # print(dictionary[column.name])
            dictionary[column.name] = getattr(self, column.name)
        return dictionary



with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")
# @app.route("/random", methods=["GET"])
# def get_random_cafe():
#   pass

## But GET is allowed by default on all routes.
# So this is much simpler:

# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    alsc = result.scalars()

    random_cafe =random.choice(all_cafes)
    print(result)
    print(all_cafes)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })

@app.route("/all")
def get_all_cafe():
    # import pandas as pd
    # data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 28], 'City': ['New York', 'London', 'Paris']}
    # df = pd.DataFrame(data)
    # series_dict = df.to_dict('series')
    # print(series_dict)

    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    # print(all_cafes)
    # print([cafe.to_dict() for cafe in all_cafes]) #(jsonify(cafe = [cafe.to_dict() for cafe in all_cafes]))
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


# @app.route("/all")
# def get_all_cafes():
#     result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
#     all_cafes = result.scalars().all()
#     #This uses a List Comprehension but you could also split it into 3 lines.
#     return jsonify(cafes=[dict(cafe) for cafe in all_cafes])
    # for i in all_cafes:
    #     return jsonify(cafe={
    #         "id": i.id,
    #         "name": i.name,
    #         "map_url": i.map_url,
    #         "img_url": i.img_url,
    #         "location": i.location,
    #         "seats": i.seats,
    #         "has_toilet": i.has_toilet,
    #         "has_wifi": i.has_wifi,
    #         "has_sockets": i.has_sockets,
    #         "can_take_calls": i.can_take_calls,
    #         "coffee_price": i.coffee_price,
    #      })
# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record
@app.route("/search")
def cafe_search():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()
    # print(query_location)
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

@app.route("/add", methods=["POST"])
def post_new_cafe():
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
    print(request.form)
    print(request.form.get("name"))
    print(request.form.get("map_url"))
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}),200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}),400


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.get_or_404(Cafe, cafe_id)
        print(cafe)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

if __name__ == '__main__':
    app.run(debug=True)
    print(__name__)
