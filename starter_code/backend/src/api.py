import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS,cross_origin

# print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

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
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
@cross_origin()
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]
    return jsonify({
        'success':True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks_all = Drink.query.all()
    drinks = [drink.long() for drink in drinks_all]
    return jsonify ({
        "success": True ,
        "drinks": drinks,     
      })
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
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

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
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


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
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
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False,
        "error":404,
        "message":"resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
