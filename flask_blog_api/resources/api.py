# -*- coding: utf-8 -*-
"""The api definition."""
from flask import Blueprint
from flask_restful import Resource
from flask_login import login_required


blueprint = Blueprint('resources', __name__)


class Users(Resource):
    #@login_required
    def get(self):
        return {
            'users': 'all'
        }

class User(Resource):
    #@login_required
    def get(self, name):
        return {
            'user': name
        }

class Posts(Resource):
    #@login_required
    def get(self, name):
        return {
            'posts': 'all'
        }

class Post(Resource):
    #@login_required
    def get(self, name, id):
        return {
            'user': name,
            'post': id
        }
