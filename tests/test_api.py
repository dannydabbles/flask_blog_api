# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import json
import pytest

from flask_blog_api.user.models import Role, User, Post


@pytest.mark.usefixtures("db")
class TestAPI:
    """API tests."""

    def test_api_test(self, testapp):
        """Test"""
        username = "foo"
        email = "foo@bar.com"
        password = "thisisatest"
        user = User(username=username, email=email, password=password)
        user.save()
        testapp.authorization = ('Basic', (user.username, password))
        response = testapp.get("/api/v0/users")
        users_data = json.loads(response.body)["users"]
        assert any([u['username'] == username for u in users_data])
        assert any([u["email"] == email for u in users_data])
        assert user.check_password(password)

    def test_users_api(self, testapp):
        """Test users endpoints"""
        # Create a user for auth
        username = "barqux"
        email = "bar@qux.com"
        password = "barquxpass"
        user = User(username=username, email=email, password=password)
        user.save()
        testapp.authorization = ('Basic', (user.username, password))

        # Create a new user via the API
        data = {
                "username": "foo",
                "email": "foo@bar.com",
                "password": "thisisatest",
                "first_name": "foo",
                "last_name": "bar",
                "is_admin": False,
        }
        response = testapp.post_json("/api/v0/users", data)
        assert response.json["username"] == data["username"]
        assert response.json["email"] == data["email"]
        assert response.json["first_name"] == data["first_name"]
        assert response.json["last_name"] == data["last_name"]
        assert response.json["is_admin"] == data["is_admin"]

        # Validate our user data from the API
        user = User.query.filter_by(username=data['username']).first()
        response = testapp.get("/api/v0/users", data)
        users_data = json.loads(response.body)["users"]
        assert any([u['username'] == data['username'] for u in users_data])
        assert any([u["email"] == data["email"] for u in users_data])
        assert user.check_password(data['password'])

        # Create a user for auth
        username = "quxfoo"
        email = "qux@foo.com"
        password = "quxfoopass"
        user = User.create(username=username, email=email, password=password)
        user.save()
        testapp.authorization = ('Basic', (user.username, password))

        # Get our auth user data
        response = testapp.get(f"/api/v0/users/{username}")
        assert response.json["username"] == username
        assert response.json["email"] == email
        assert user.check_password(password)

        # Update our auth user data
        email = "qux2@foo.com"
        response = testapp.put_json(
            f"/api/v0/users/{username}",
            {
                'username': username,
                'email': email,
            }
        )
        assert response.json["email"] == email
        response = testapp.get(f"/api/v0/users/{username}")
        assert response.json["email"] == email

        # Delete our user
        response = testapp.get(f"/api/v0/users/{username}")
        assert response.status_code == 200
        assert response.json['username'] == username
        response = testapp.delete(f"/api/v0/users/{username}")
        assert response.status_code == 200
        assert User.query.filter_by(username=username).first() is None

    def test_posts_api(self, testapp):
        """Test posts endpoints"""
        # Create a user for auth
        username = "barqux"
        email = "bar@qux.com"
        password = "barquxpass"
        user = User.create(username=username, email=email, password=password)
        user.save()
        testapp.authorization = ('Basic', (user.username, password))

        # Create some posts
        response = testapp.post_json(
            f"/api/v0/users/{username}/posts",
            {
                'title': 'post title',
                'content': 'post content',
                'active': False
            }
        )

        # Get our post
        response = testapp.get(f"/api/v0/users/{username}/posts")
        assert len(response.json['posts']) == 1

        # Create some more posts
        for i in range(10):
            response = testapp.post_json(
                f"/api/v0/users/{username}/posts",
                {
                    'title': f"post title{i}",
                    'content': f"post content{i}",
                    'active': True
                }
            )
        response = testapp.get(f"/api/v0/users/{username}/posts")
        assert len(response.json['posts']) == 11

        # Update our posts
        posts = Post.query.all()
        for post in posts:
            response = testapp.get(f"/api/v0/users/{username}/posts/{post.id}")
            assert response.json['post']['title'].startswith('post title')
            assert response.json['post']['content'].startswith('post content')
            response = testapp.put_json(
                f"/api/v0/users/{username}/posts/{post.id}",
                {
                    'title': f"new post title",
                    'content': f"new post content",
                    'active': True
                }
            )
            response = testapp.get(f"/api/v0/users/{username}/posts/{post.id}")
            assert response.json['post']['title'].startswith('new post title')
            assert response.json['post']['content'].startswith('new post content')
        response = testapp.get(f"/api/v0/users/{username}/posts")
        assert len(response.json['posts']) == 11

        # Delete our posts
        for post in posts:
            assert Post.query.filter_by(id=post.id).first() is not None
            response = testapp.delete(f"/api/v0/users/{username}/posts/{post.id}")
            assert response.status_code == 200
            assert Post.query.filter_by(id=post.id).first() is None
        response = testapp.get(f"/api/v0/users/{username}/posts")
        assert response.status_code == 200
        assert len(response.json['posts']) == 0
