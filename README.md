# Modern Research Data Portal - mrdp
Simple web app framework for the exercises in the MRDP workshop. It is based on [bottle](http://bottlepy.org) and uses [beaker](https://www.github.com/bbangert/beaker) with [pycrypto](http://www.dlitz.net/software/pycrypto) for encrypted session management.

All exercise code should be added to the `mrdp_app.py` file. The following routes are currently available:
/login - gets an authenticated user from Globus Auth
/logout - deletes authenticated user credentials
/repository - displays a listing of available datasets in the repository
/download - transfers selected dataset from repository to destination endpoint
/browse/<target_uri> - lists the files in the dataset identfied by <target_uri>
/status/<task_id> - gets status of transfer with <task_id>

HTML templates are in the /views directory. Do not modify `base.tpl`, `header.tpl`, `footer.tpl`, and `scripts.tpl`.

All styling related code (including fonts and images) is in the /static directory.

### Getting/setting session variables
To set a session variable use: `request.session['my_key'] = value`
To get a session variable use: `request.session['my_key']`

