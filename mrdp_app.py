# Copyright (C) 2016 University of Chicago
#
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import uuid
import datetime
from bottle import route, request, response, redirect, template, static_file, hook

'''
Set up static resource handler - DO NOT CHANGE THIS METHOD IN ANY WAY
-----------------------------------------------------------------------------
'''
@route('/static/<filename:path>', method='GET', name="static")
def serve_static(filename):
  # Tell Bottle where static files should be served from
  return static_file(filename, 
    root=request.app.config['mrdp.env.static_root'])


'''
Configure request hooks.
- Make the beaker session available
- Add CORS support
-----------------------------------------------------------------------------
'''
@hook('before_request')
def expose_session():
    request.session = request.environ.get('beaker.session')

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'


'''
Home page - play with it if you must!
-----------------------------------------------------------------------------
'''
@route('/', method='GET', name="home")
def home_page():
  return template(request.app.config['mrdp.env.templates'] + 'home',
  	authenticated_user=False)


'''
Add all MRDP application code below
-----------------------------------------------------------------------------
'''
@route('/login', method='GET', name="login")
def login():
  '''
  Add code here to redirect user to Globus Auth
  When returning an authenticated user, redirect to the repository page
  '''
  
  redirect('/repository')


@route('/logout', method='GET', name="logout")
def logout():
	pass


test_dataset = [{'name': 'Dataset one', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset two', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset three', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset four', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset five', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset six', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset seven', 'uri': str(uuid.uuid4())}]

@route('/repository', method='GET', name="repository")
def repository():
  '''
  Add code here to:
  - Check that we have an authenticated user (i.e. don't allow
    unauthenticated users to access the repository)
  - Get a list of the datasets in the repository
  - Display a dataset list so user can browse/select to download
  '''
  return template(request.app.config['mrdp.env.templates'] + 'repository', 
  	authenticated_user=True, 
  	datasets=test_dataset)


@route('/download', method='POST', name="download")
def download():
  '''
  Add code here to:
  - Send to Globus to select a destination endpoint
  - Submit a Globus transfer request and get the task ID
  - Return to a transfer "status" page
  '''

  return template(request.app.config['mrdp.env.templates'] + 'transfer_status', 
  	authenticated_user=True, 
  	task_id=str(uuid.uuid4()),
  	transfer_status=None)


test_file_list = [{'name': 'File Number One', 'size': 213514, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number two', 'size': 123525, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number three', 'size': 21343, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number four', 'size': 234235, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number five', 'size': 90835, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number six', 'size': 28722, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number seven','size': 765324, 'uri': str(uuid.uuid4())}]

@route('/browse/<target_uri>', method='GET', name="browse")
def browse(target_uri):
  '''
  Add code here to:
  - Get list of files for the selected dataset
  - Return a list of files to a browse view
  '''

  return template(request.app.config['mrdp.env.templates'] + 'browse', 
  	authenticated_user=True, 
  	dataset_uri=target_uri,
  	file_list=test_file_list)


test_transfer_status = {'source_ep_name': 'XSEDE Keeneland',
  'dest_ep_name': 'UChicago RCC Midway',
  'request_time': datetime.datetime.now() - datetime.timedelta(days=1),
  'status': 'ACTIVE',
  'files_transferred': 5005,
  'faults': 0}

@route('/status/<task_id>', method="POST", name="transfer_status")
def transfer_status(task_id):
	'''
	Add code here to:
	- Call Globus to get status/details of transfer with task_id
	'''

	return template(request.app.config['mrdp.env.templates'] + 'transfer_status', 
		authenticated_user=True, 
		task_id=task_id,
		transfer_status=test_transfer_status)


### EOF