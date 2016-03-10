# Modern Research Data Portal - mrdp
Simple web app framework for the exercises in the MRDP workshop. It is based on the [Bottle](http://bottlepy.org) microframework and uses [Beaker](http://beaker.readthedocs.org/en/latest/) with [PyCrypto](https://github.com/dlitz/pycrypto) for encrypted session management. Since the MRDP requires HTTPS (so it can integrate with Globus Auth) we use the [CherryPy](http://www.cherrypy.org/) server with the [PyOpenSSL](http://www.pyopenssl.org/en/stable/) module to serve the application.

## Setting up the environment
You may need the following prerequisites (shown for Ubuntu):
```
apt-get install python-setuptools python-dev build-essential python-pip unzip --assume-yes
apt-get install libssl-dev libffi-dev --assume-yes
apt-get install python-cherrypy3 --assume-yes
```

CherryPy requires that an SSL certificate is available (for the correct hostname). The path to the certificate and corresponding key must be specified in the the `MRDP_APP_SSL_CERT_PATH` and `MRDP_APP_SSL_KEY_PATH` environment variables respectively (change these in `mrdp_run.sh`).

Assuming you have [pip](https://pip.pypa.io/en/stable/) available, run the following to install the required packages:
```
pip install --upgrade bottle
pip install --upgrade beaker
pip install --upgrade pycrypto
pip install --upgrade pyopenssl
pip install --upgrade cherrypy
```

## Running the app server
As configured, the server listens on port 443 (HTTPS) and accepts connections from anywhere (i.e. 0.0.0.0/0). Start the server by running `mrdp_run.sh`. The host and port parameters are exported as environment variables in the script.

## Coding notes
All exercise code should be added to the `mrdp_app.py` file. The following routes are currently available:

- `/login` - gets an authenticated user from Globus Auth
- `/logout` - deletes authenticated user credentials
- `/repository` - displays a listing of available datasets in the repository
- `/download` - transfers selected dataset from repository to destination endpoint
- `/browse/<target_uri>` - lists the files in the dataset identfied by `<target_uri>`
- `/status/<task_id>` - gets status of transfer with `<task_id>`

Each route has some placeholder variables (prefixed by 'test_') used for testing purposes. These must be removed and replaced by real code. 

HTML templates are in the /views directory. Do not modify `base.tpl`, `header.tpl`, `footer.tpl`, and `scripts.tpl` unless you're familiar with the bottle template structure. The other templates may be modified 

All styling related code (including fonts and images) is in the /static directory. Pleaase don't move static files around unless you're familiar with how Bottle resolves static references.

To set a session variable use `request.session['my_key'] = value`. Get a session variable as `request.session['my_key']`. An example is provided in `transfer_status`.

