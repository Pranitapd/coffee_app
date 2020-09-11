import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS,cross_origin

# print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth #remove do before first auth to remove Import error

app = Flask(__name__)
setup_db(app)
# CORS(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH')
    return response


# db_drop_and_create_all()


@app.route('/drinks')
@cross_origin()
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]
    if len(drinks) == 0:
        abort(404)
    return jsonify({
        'success':True,
        'drinks': drinks
    })



@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks_all = Drink.query.all()
    drinks = [drink.long() for drink in drinks_all]
    if len(drinks)==0:
        abort(404)
    return jsonify ({
        "success": True ,
        "drinks": drinks,     
      })


@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    try:
        body = request.get_json()
        recipe = body.get('recipe', None)
        title = body.get('title', None)

        new_drink = Drink(title=title , recipe=json.dumps(recipe))
        new_drink.insert()
        drinks_all = Drink.query.all()
        drinks = [drink.long() for drink in drinks_all]
        return jsonify ({
            "success": True ,
            "drinks": drinks,     
        })
    except:
        abort(405)



@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt,drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    
    head = request.get_json(force=True)
    drink.title = json.dumps(head.get('title', drink.title))
    drink.recipe = json.dumps(head.get('recipe'))
    drink.update()

    return jsonify({
        'success':True,
        "drinks": (Drink.query.get(drink_id)).long()
    })



@app.route('/drinks/<int:drink_id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt,drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    drink.delete()

    return jsonify({
        "success":True,
        "drink":drink_id
    })

## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False,
        "error":404,
        "message":"resource not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success":False,
        "error":405,
        "message":"method not allowed"
    })


@app.errorhandler(AuthError)
def handle_auth_error(e):
    response = jsonify(e.error)
    response.status_code = e.status_code
    return response
