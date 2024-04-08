from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
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
        # dictionary = {}
        # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     #Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary
        
        #Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(result)
      
    # return jsonify(Cafe = {
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    #     })
    
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/get")
def get_all_cafe():
    all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name) ).scalars().all()    
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])   


@app.route('/search')
def search_cafe_location():
    location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location==location)).scalars().all()
    if result:
        return jsonify(cafes=[cafe.to_dict() for cafe in result])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
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
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

# HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>',  methods=["PATCH"])
def patch(cafe_id):
    new_price = request.args.get('new_price')
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else :
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    

# HTTP DELETE - Delete Record
api_key = 'TopSecretAPIKey'
@app.route('/report-close/<int:cafe_id>', methods=['DELETE', 'GET']) #se le coloca get para hacerlo desde el navegador tambien, en postman se puede omitir el get
def delete_cafe(cafe_id):
    api_key_user = request.args.get('api-key')
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if api_key_user == api_key and cafe:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(error={'Seccess' : 'Successfully deleted Cafe'}), 200
    elif cafe: 
        return jsonify(response = {"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        
        

if __name__ == '__main__':
    app.run(debug=True)
