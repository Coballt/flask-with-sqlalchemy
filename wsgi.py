try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass # Heroku does not use .env
import json
from flask import Flask, jsonify, request, render_template
from config import Config
app = Flask(__name__)
app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow # Order is important here!
db = SQLAlchemy(app)
ma = Marshmallow(app)

from models import Product
from schemas import products_schema, product_schema

@app.route('/')
def hello():
    products = db.session.query(Product).all()
    return render_template('home.html', products=products)

@app.route('/products/<int:id>')
def show_product(id):
    product = db.session.query(Product).get(id)
    return render_template('product.html', product=product)

@app.route('/api/v1/products')
def products():
    products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
    return products_schema.jsonify(products)

@app.route('/api/v1/products/<int:id>')
def get_products(id):
    products = db.session.query(Product).get(id)
    if products is not None :
        return product_schema.jsonify(products)
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/v1/products', methods=['POST'])
def post_products():
    try:
        payload = json.loads(request.data)
    except ValueError :
        return jsonify({"error" : "Bad payload received"}), 422
    if 'name' not in payload or 'description' not in payload:
        return jsonify({"error" : "Bad payload received"}), 422
    product = Product(name=payload['name'], description=payload['description'])
    db.session.add(product)
    db.session.flush()
    db.session.commit()
    return product_schema.jsonify(product), 201

@app.route('/api/v1/products/<int:id>', methods=['DELETE'])
def delete_products(id):
    product = db.session.query(Product).get(id)
    if product is not None :
        db.session.delete(product)
        db.session.flush()
        db.session.commit()
        return '', 204
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/v1/products/<int:id>', methods=['PATCH'])
def update_products(id):
    try:
        payload = json.loads(request.data)
    except ValueError :
        return jsonify({"error" : "Bad payload received"}), 422
    if 'name' not in payload and 'description' not in payload:
        return jsonify({"error" : "Bad payload received"}), 422
    product = db.session.query(Product).get(id)
    if product is not None :
        if 'name' in payload:
            product.name = payload['name']
        if 'description' in payload:
            product.description = payload['description']
        db.session.commit()
        return '', 204
    return jsonify({"error": "Product not found"}), 404
