# -*- coding: utf-8 -*-
"""The api definition."""
from flask import Blueprint
from flask_restful import Resource, reqparse
from flask_blog_api.user.models import User as UserModel
from flask_blog_api.user.models import Post as PostModel

blueprint = Blueprint('resources', __name__)


class Users(Resource):
    def get(self):
        return {
            'users': [str(user) for user in UserModel.query.all()]
        }


class User(Resource):
    def get(self, name):
        return {
            'user': name
        }


class Posts(Resource):
    def get(self, name):
        return {
            'posts': [str(post) for post in PostModel.query.all()]
        }

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        args = parser.parse_args(strict=True)
        user = UserModel.create(
            username=args['username'],
            email=args['email'],
            password='testtest',
            first_name='Test',
            last_name='Testing',
            is_admin=True,
        )
        return str(user), 200


class Post(Resource):
    def get(self, name, id):
        return {
            'posts': [str(post) for post in
                      PostModel.query.filter_by(user=UserModel.query.filter_by(username=name).id, id=id)]
        }
