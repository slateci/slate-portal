[![Build Status](https://travis-ci.org/globus/globus-sample-data-portal.svg?branch=master)](https://travis-ci.org/globus/globus-sample-data-portal)

# SLATE Portal
Web portal to the SLATE [platform](https://www.portal.slateci.io/).

## Overview
This repository contains the SLATE portal applications. The "Portal," utilizes Globus in order to to authenticate users with [Auth](https://docs.globus.org/api/auth/). All of the Portal code can be found in the `portal/` directory.

## Getting Started
#### Set up your environment.
* [OS X](#os-x)

#### Create your own App registration for use in the Portal. 
* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you'll be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you'll be asked for some information, including the redirect URL and any scopes you will be requesting.
    * Redirect URL: `https://localhost:5000/authcallback` (note: if using EC2 `localhost` should be replaced with the IP address of your instance).
    * Scopes: `urn:globus:auth:scope:transfer.api.globus.org:all`, `openid`, `profile`, `email`
* After creating your App the client id and secret can be copied into this project in the following two places:
    * `portal/portal.conf` in the `PORTAL_CLIENT_ID` and `PORTAL_CLIENT_SECRET` properties.
    * `service/service.conf` where the `PORTAL_CLIENT_ID` is used to validate the access token that the Portal sends to the Service.

### OS X

##### Environment Setup

* `sudo easy_install pip`
* `sudo pip install virtualenv`
* `sudo mkdir ~/projects`
* `cd ~/projects`
* `git clone https://github.com/slateci/slate-portal.git`
* `cd slate-portal`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `mkdir instance`
* `touch instance/portal.conf`
* Note that current `portal.conf` file located in `slate-portal/portal/portal.conf` is the default .conf file from the Globus Developer Portal. SLATE Portal will real from the new `instance/portal.conf` file.
* New `instance/portal.conf` file should be updated with new/correct API keys.

##### Running the Portal App

* `./run_portal.py`
* point your browser to `https://localhost:5000`