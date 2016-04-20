# Modern Research Data Portal - mrdp
Simple web app framework for the exercises in the GlobusWorld developer workshop.

## Getting Started

### OS X

##### Environment Setup

* `sudo easy_install pip`
* `sudo pip install virtualenv`
* `git clone https://github.com/globus/globus-sample-data-portal`
* `cd globus-sample-data-portal`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`

##### Running the Portal App

* `./run_portal.py`

### Linux (Ubuntu)

##### Environment Setup

* `sudo apt-get update`
* `sudo apt-get install python-pip`
* `sudo pip install virtualenv`
* `sudo apt-get install git`
* `git clone https://github.com/globus/globus-sample-data-portal`
* `cd globus-sample-data-portal`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`

##### Running the Portal App

* `./run_portal.py`

### Windows

##### Environment Setup

* Install Python (<https://www.python.org/downloads/windows/>)
* `pip install virtualenv`
* Install git (<https://git-scm.com/downloads>)
* `git clone https://github.com/globus/globus-sample-data-portal`
* `cd globus-sample-data-portal`
* `virtualenv venv`
* `venv\Scripts\activate`
* `pip install -r requirements.txt`

##### Running the Portal App

* `python run_portal.py`

### Globus-Provided AWS Instance

At the Globus World workshop, you will be given an IP address, username, and
password. Using these, open an ssh connection to the remote instance.

Once connected, run the commands below, substituting `YOUR_IP` as required.

##### Environment Setup

* `git clone https://github.com/globus/globus-sample-data-portal`
* `cd globus-sample-data-portal`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `sed -i 's/localhost/0.0.0.0/' run_*.py`
* `sed -i '4,//s/localhost/YOUR_IP/' */*.conf`

##### Running the Portal App

* `./run_portal.py`
* point your web browser to `https://YOUR_IP:5000/`
