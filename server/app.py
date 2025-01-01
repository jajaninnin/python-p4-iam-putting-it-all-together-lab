#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        params = request.json
        try:
            username = params.get('username')
            password = params.get('password')
            image_url = params.get('image_url')
            bio = params.get('bio')

            if not username or not password or not image_url or not bio:
                return make_response({'error': 'Missing required fields'}, 422)
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return make_response({'error': 'Username already exists'}, 422)

            user = User(username=username, password_hash=password, image_url=image_url, bio=bio)

            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return make_response(user.to_dict(), 201)

        except Exception as e:
            print(f'error occured: {e}')
            return make_response({'error': 'failed to sign up'})

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if user:
                return make_response(user.to_dict(), 200)
        return make_response({'error': 'Not Authorized'}, 401)

class Login(Resource):
    def post(self):
        params = request.json

        user = params.get('username')
        password = params.get('password')

        if not user or not password:
            return make_response({'error': 'Username and password are required'}, 401)
        
        user = db.session.query(User).filter_by(username=user).first()

        if not user:
            return make_response({'error': 'user not found'}, 401)

        if user.authenticate(password):
            session['user_id'] = user.id
            return make_response(user.to_dict(), 200)
        else:
            print('invalid password')
            return make_response({'error': 'invalid password'}, 401)

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if user_id:
            session.pop('user_id', None)
            return make_response({}, 204)
        else:
            return make_response({'error': 'Not Authorized'}, 401)

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            recipes = db.session.execute(db.select(Recipe)).scalars()
            rsp_recipes = [rcp.to_dict() for rcp in recipes]
            return make_response(rsp_recipes, 200)
        else:
            return make_response({'error': 'Not Authorized'}, 401)
    
    def post(self):
        user_id = session.get('user_id')
        if user_id:
            try:
                params = request.json
                new_recipe = Recipe(
                    title=params.get('title'),
                    instructions=params.get('instructions'),
                    minutes_to_complete=params.get('minutes_to_complete'),
                    user_id=user_id
                )
                db.session.add(new_recipe)
                db.session.commit()
                return make_response(new_recipe.to_dict(), 201)
            except Exception as e:
                return make_response({'error': 'unprocessable entiuty'}, 422)
        else:
            return make_response({'error': 'Not Authorized'}, 401)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)