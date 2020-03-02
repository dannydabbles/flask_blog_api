# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import json
import pytest

from flask_blog_api.extensions import bcrypt

from flask_blog_api.user.models import Role, User

from .factories import UserFactory

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
        users_data = json.loads(response.body)["users"][0]
        assert users_data["username"] == username
        assert users_data["email"] == email
        assert user.check_password(password)
        user.delete()
