# Copyright (C) 2016 University of Chicago
#
__author__ = 'Globus Team <info@globus.org>'

import uuid
import datetime
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config.from_pyfile('mrdp.conf')


'''
Home page - play with it if you must!
-----------------------------------------------------------------------------
'''
@app.route('/', methods=['GET'])
def home():
  return render_template('home.jinja2')


'''
Some dummy data for testing
-----------------------------------------------------------------------------
'''
test_datasets = [
  {'name': 'Dataset one', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset two', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset three', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset four', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset five', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset six', 'uri': str(uuid.uuid4())}, 
  {'name': 'Dataset seven', 'uri': str(uuid.uuid4())}
]
test_task_id = str(uuid.uuid4())
test_file_list = [
  {'name': 'File Number One', 'size': 213514, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number two', 'size': 123525, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number three', 'size': 21343, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number four', 'size': 234235, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number five', 'size': 90835, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number six', 'size': 28722, 'uri': str(uuid.uuid4())}, 
  {'name': 'File Number seven','size': 765324, 'uri': str(uuid.uuid4())}
]
test_transfer_status = {
  'source_ep_name': 'XSEDE Keeneland',
  'dest_ep_name': 'UChicago RCC Midway',
  'request_time': datetime.datetime.now() - datetime.timedelta(days=1),
  'status': 'ACTIVE',
  'files_transferred': 2354,
  'faults': 0
}


'''
Add all MRDP application code below
-----------------------------------------------------------------------------
'''
@app.route('/login', methods=['GET'])
def login():
  '''
  Add code here to:
  - Redirect user to Globus Auth
  - Get an access token and a refresh token
  - Store these tokens in the session
  - Redirect to the repository page
  '''
  # Used for test purposes; replace with real code
  session['globus_auth_token'] = str(uuid.uuid4())
  session['username'] = 'devuser'
  
  return redirect(url_for('home'))


@app.route('/logout', methods=['GET'])
def logout():
  '''
  Add code here to:
  - Destroy Globus Auth token (remove it from session?)
  - ???
  '''
  # Used for test purposes; replace with real code
  session.pop('globus_auth_token', None)

  return redirect(url_for('home'))


@app.route('/repository', methods=['GET'])
def repository():
  '''
  Add code here to:

  - Check that we have an authenticated user (i.e. don't allow
    unauthenticated users to access the repository)
  - Get a list of the datasets in the repository
  - Display a dataset list so user can browse/select to download

  The target template (repository.tpl) expects 'datasets' 
  (list of dictionaries) that describe each dataset as:
  {'name': 'dataset name', 'uri': 'dataset uri/path'}

  If you want to display additional information about each
  dataset, you must add those keys to the dictionary 
  and modify the repository.tpl template accordingly.

  '''

  return render_template('repository.jinja2', datasets=test_datasets)


@app.route('/download', methods=['POST'])
def download():
  # Get a list of the selected datasets
  datasets = request.form.getlist('dataset')
  # Get the selected year to filter the dataset
  year_filter = request.form.get('year_filter') 

  '''
  Add code here to:

  - Send to Globus to select a destination endpoint
  - Submit a Globus transfer request and get the task ID
  - Return to a transfer "status" page

  The target template expects a 'task_id' (str) and a 
  'transfer_status' (dictionary) containing various details 
  about the task. Since this route is called only once after 
  a transfer request is submitted, it only provides a 'task_id'.
  '''

  return render_template('transfer_status.jinja2', task_id=test_task_id,
                         transfer_status=None)


@app.route('/browse/<target_uri>', methods=['GET'])
def browse(target_uri):
  '''
  Add code here to:

  - Get list of files for the selected dataset
  - Return a list of files to a browse view

  The target template (browse.tpl) expects a unique dataset identifier 
  'dataset_uri' (str) and 'file_list' (list of dictionaries) containing 
  the following information about each file in the dataset:
  {'name': 'file name', 'size': 'file size', 'uri': 'file uri/path'}

  'dataset_uri' is passed to the route in the URL as 'target_uri'.

  If you want to display additional information about each
  file, you must add those keys to the dictionary 
  and modify the browse.tpl template accordingly.

  '''

  return render_template('browse.jinja2', dataset_uri=target_uri,
                         file_list=test_file_list)


@app.route('/status/<task_id>', methods=["POST"])
def transfer_status(task_id):
  '''
  Add code here to call Globus to get status/details of transfer
  with task_id.

  The target template (tranfer_status.tpl) expects a 'task_id' (str) 
  and a 'transfer_status' (dictionary) containing various details 
  about the task. 'transfer_status' is expected to contain the 
  following keys:
  {'source_ep_name': 'display name of source endpoint',
   'dest_ep_name': 'display name of destination endpoint',
   'request_time': time that the transfer request was submitted,
   'status': 'status of the transfer task',
   'files_transferred': number of files transferred so far,
   'fault': number of faults encountered}

  'task_id' is passed to the route in the URL as 'task_id'.

  If you want to display additional information about the
  transfer, you must add those keys to the dictionary 
  and modify the transfer_status.tpl template accordingly.
  '''

  return render_template('transfer_status.jinja2', task_id=task_id,
                         transfer_status=test_transfer_status)


if __name__ == '__main__':
    app.run()


### EOF
