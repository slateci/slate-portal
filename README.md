# Modern Research Data Portal - mrdp
Simple web app framework for the exercises in the MRDP workshop. It is based on the [Bottle](http://bottlepy.org) microframework and uses [Beaker](http://beaker.readthedocs.org/en/latest/) with [PyCrypto](https://github.com/dlitz/pycrypto) for encrypted session management.

All exercise code should be added to the `mrdp_app.py` file. The following routes are currently available:

- `/login` - gets an authenticated user from Globus Auth
- `/logout` - deletes authenticated user credentials
- `/repository` - displays a listing of available datasets in the repository
- `/download` - transfers selected dataset from repository to destination endpoint
- `/browse/<target_uri>` - lists the files in the dataset identfied by `<target_uri>`
- `/status/<task_id>` - gets status of transfer with `<task_id>`

### Setting up the environment
Assuming you're in a [virtualenv](http://virtualenv.readthedocs.org/en/latest/index.html) that has [pip](https://pip.pypa.io/en/stable/) available, run the following to install the prerequisite packages:
```
pip install --upgrade bottle
pip install --upgrade beaker
pip install --upgrade pycrypto
```

### Running the app server
As configured, the server listens on port 8888 and accepts connections from anywhere (i.e. 0.0.0.0/0). Start the server by running `mrdp_run.sh`. The host and port parameters are exported as environment variables in the script. You can change the port number but do not use a reserved port (e.g. port 80) or you will run into permission issues.

### Coding notes
Each route has some placeholder variables (prefixed by 'test_') used for testing purposes. These must be removed and replaced by real code. 

HTML templates are in the /views directory. Do not modify `base.tpl`, `header.tpl`, `footer.tpl`, and `scripts.tpl` unless you're familiar with the bottle template structure. The other templates may be modified 

All styling related code (including fonts and images) is in the /static directory. Pleaase don't move static files around unless you're with how Bottle resolves static references.

#### Getting/setting session variables
To set a session variable use: `request.session['my_key'] = value`

To get a session variable use: `request.session['my_key']`

