# Copyright (C) 2015 University of Chicago
#
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import os
import sys
from bottle import app, SimpleTemplate, run
from bottle import ServerAdapter, server_names
from beaker.middleware import SessionMiddleware

'''
*******************************************************************************
Configure application
DO NOT MODIFY THIS BLOCK - Use environment variables to make changes
*******************************************************************************
'''
def config_app(app):
	# Load application configuration
	config_path = os.path.dirname(os.path.abspath(__file__))
	app.config.load_config(config_path + '/' + 'mrdp.conf')

	# Add environment variable-based settings
	app.config['mrdp.env.host'] = os.environ['MRDP_APP_HOST']
	app.config['mrdp.env.port'] = os.environ['MRDP_APP_PORT']
	app.config['mrdp.env.static_root'] = os.environ['MRDP_STATIC_ROOT']
	app.config['mrdp.env.templates'] = os.environ['MRDP_TEMPLATES_ROOT']
	app.config['mrdp.env.debug'] = False or os.environ['MRDP_DEBUG']

	return (app)

'''
*******************************************************************************
Main
*******************************************************************************
'''
if __name__ == '__main__':

	# Create a Bootle app instance
	app = app()

	# Set app configuration
	app = config_app(app)

	# Enable get_url function to be used inside templates to lookup static files
	SimpleTemplate.defaults['get_url'] = app.get_url
	SimpleTemplate.defaults['debug'] = app.config['mrdp.env.debug']

	# Import the application routes (controllers)
	import mrdp_app

	# Add session middleware to the Bottle app
	# NOTE: After wrapping the Bottle app in SessionMiddleware, use app.wrap_app to
	# access any of the Bottle objects such as "config"
	session_options = {'session.type': 'cookie',
										 'session.cookie_expires': True,
										 'session.timeout': app.config['mrdp.session.timeout'],
										 'session.encrypt_key': app.config['mrdp.session.encrypt_key'],
										 'session.validate_key': app.config['mrdp.session.validate_key'],
										 'session.httponly': True,
										 'session.auto': True}
	app = SessionMiddleware(app, session_options)

	# Start WSGI server; uses default Bootle server - Change this for production use!
	run(app=app,
			host=app.wrap_app.config['mrdp.env.host'],
			port=app.wrap_app.config['mrdp.env.port'],
			debug=app.wrap_app.config['mrdp.env.debug'],
			reloader=True,
			server="wsgiref")
