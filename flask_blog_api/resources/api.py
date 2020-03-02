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
            'users': [user.as_dict() for user in UserModel.query.all()]
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('first_name', type=str, required=True)
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('is_admin', type=bool, required=True)
        args = parser.parse_args(strict=True)
        user = UserModel.create(
            username=args['username'],
            email=args['email'],
            password=args['password'],
            first_name=args['first_name'],
            last_name=args['last_name'],
            is_admin=bool(args['is_admin']),
        )
        return user.as_dict(), 200


class User(Resource):
    def get(self, username):
        user = UserModel.query.filter_by(username=username).first()
        return user.as_dict(), 200

    def delete(self, username):
        user = UserModel.query.filter_by(username=username).first()
        user.delete()
        return {}, 200

    def put(self, username):
        user = UserModel.query.filter_by(username=username).first()
        if user is None:
            raise Exception(f"ERROR: Can not update non-existent user {username}")
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, default=user.email)
        parser.add_argument('email', type=str, default=user.email)
        parser.add_argument('password', type=str, default=user.password)
        parser.add_argument('first_name', type=str, default=user.first_name)
        parser.add_argument('last_name', type=str, default=user.last_name)
        parser.add_argument('is_admin', type=bool, default=user.is_admin)
        args = parser.parse_args(strict=True)

        user = user.update(
            username=args['username'],
            email=args['email'],
            password=args['password'],
            first_name=args['first_name'],
            last_name=args['last_name'],
            is_admin=args['is_admin'],
        )
        return user.as_dict(), 201


class Posts(Resource):
    def get(self, username):
        posts = PostModel.query.filter_by(
            user_id=UserModel.query.filter_by(
                username=username
            ).first().id
        )
        if posts is None:
            return {}

        return {
            'posts': [post.as_dict() for post in posts]
        }

    def post(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        parser.add_argument('active', type=bool, required=True)
        args = parser.parse_args(strict=True)
        post = PostModel.create(
            user=UserModel.query.filter_by(username=username).first(),
            title=args['title'],
            content=args['content'],
            active=bool(args['active']),
        )
        return post.as_dict(), 200


class Post(Resource):
    def get(self, username, id):
        post = PostModel.query.filter_by(
            user_id=UserModel.query.filter_by(
                username=username
            ).first().id,
            id=id,
        ).first()
        return {
            'post': post.as_dict()
        }

    def delete(self, username, id):
        user = UserModel.query.filter_by(username=username).first()
        post = PostModel.query.filter_by(user_id=user.id, id=id).first()
        post.delete()
        return {}, 200

    def put(self, username, id):
        user = UserModel.query.filter_by(username=username).first()
        if user is None:
            raise Exception(f"ERROR: Can not update post #{id} non-existent user {username}")
        post = PostModel.query.filter_by(user_id=user.id, id=id).first()
        if post is None:
            raise Exception(f"ERROR: Can not update post #{id} user {username}")
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('content', type=str)
        parser.add_argument('active', type=bool)
        args = parser.parse_args(strict=True)
        post = post.update(
            title=args['title'],
            content=args['content'],
            active=args['active'],
        )
        return post.as_dict(), 201
