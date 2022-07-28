import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink #for python version 3.10.5 use from database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth #for python version 3.10.5 use from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods =['GET'])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()  
        formanted_drinks = [drink.short() for drink in drinks]

        return jsonify(
            {
                'success': True,
                'drinks': formanted_drinks
            }
        ), 200
    except:
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods = ['GET'])
@requires_auth('get:drinks-detail')
def drink_details():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        formated_drinks = [drink.long() for drink in drinks]

        return jsonify(
            {
                'success': True,
                'drinks': formated_drinks,
            }
        ), 200
    except:
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def create_drinks():
    body = request.get_json()
    recipe_data = body.get('recipe', None)
    recipe = json.dumps(recipe_data)
    try:
        new_drink = Drink(
            title = body.get('title', None),
            recipe = recipe
        )
        new_drink.insert()
        return jsonify(
            {
                'success': True,
                'drinks': [new_drink.long()]
            }
        ), 200
    except:
        abort(422)



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
@app.route('/drinks/<int:id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(id):
    drinks = Drink.query.get(id)
    if drinks is None:
        abort(404)
    body = request.get_json()
    try:
        if 'title' in body:
            drinks.title = body['title']
        elif 'recipe' in body:
            drinks.recipe = json.dumps(body['recipe'])
            
        drinks.update()
        
        return jsonify(
            {
                'success': True,
                'drinks': [drinks.long()]
            }
        ), 200
    except:
        abort(422)
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
@app.route('/drinks/<int:id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        drink.delete()
        return jsonify(
            {
                'success': True,
                'delete': id
            }
    ), 200
    except:
        abort(400)

# Error Handling
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

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            'success': False,
            'error': 404,
            'message': 'recoure not found'
        }
    ), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify(
        {
            'success': False,
            'error': error.error,
            'message': error.status_code,
        }
    ), error.status_code

@app.errorhandler(401)
def unauthorized(error):
    return jsonify(
        {
            'success': False,
            'error': 401,
            'message': 'unathorized'
        }
    ), 401
@app.errorhandler(400)
def bad_request(error):
    return jsonify(
        {
            'success': False,
            'error': 400,
            'message': 'bad request'
        }
    ), 400
@app.errorhandler(403)
def bad_request(error):
    return jsonify(
        {
            'success': False,
            'error': 403,
            'message': 'permission is not present'
        }
    ), 403
@app.errorhandler(500)
def internal_sever_error(error):
    return jsonify(
        {
            'success': False,
            'error': 500,
            'message': 'internal sever error'
        }
    ), 500
    
if __name__ == '__main__':
    app.run()
    