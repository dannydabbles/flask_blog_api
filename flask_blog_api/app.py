# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys

from flask import Flask, render_template, jsonify, make_response
from flask_blog_api import commands, public, user, resources
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth
from flask_blog_api.extensions import (
    bcrypt,
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    flask_static_digest,
    login_manager,
    migrate,
)


def create_app(config_object="flask_blog_api.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_api(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    flask_static_digest.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(resources.api.blueprint)
    return None


def register_api(app):
    """Register REST API endpoints"""
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        verify_user = user.models.User.query.filter_by(username=username).first()
        if not verify_user:
            return False
        return verify_user.check_password(password)

    @auth.error_handler
    def unauthorized():
        return make_response(jsonify(message='Unauthorized Access: Please make an account at http://0.0.0.0:5000/register/', status=403), 403)

    rest_api = Api(app, prefix="/api/v0", decorators=[csrf_protect.exempt, auth.login_required])
    rest_api.add_resource(resources.api.Users, '/users')
    rest_api.add_resource(resources.api.User,  '/users/<string:username>')
    rest_api.add_resource(resources.api.Posts, '/users/<string:username>/posts')
    rest_api.add_resource(resources.api.Post,  '/users/<string:username>/posts/<int:id>')
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db, "User": user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
