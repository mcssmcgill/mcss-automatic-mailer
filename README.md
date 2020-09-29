# mcss-automatic-mailer
Automatic membership code and emailing tool upon purchase of the MCSS Membership Card

## Setup and Installation

To get the application set up, you need the following environment variables. 
To do this, create a file called `.env` at the root of the `backend` folder, and define variables in the following format:

```
CUSTOMERS_URL=example_value
ACTIVATION_CODES_URL=example_value
AIRTABLE_API_KEY=example_value
SENDGRID_API_KEY=example_value
```
## How to Run Locally

First off, make sure to create a virtual environment on your machine. A virtual environment can be created with either `virtualenv` (python 2) or `venv` (python 3). For `venv`:

```
python3 -m venv env

source env/bin/activate
```

The second line activates the virtual environment, and you can type `deactivate` to exit the environment.

To install dependencies from a `requirements.txt` file, do this:

```
pip install -r /path/to/requirements.txt
```

You only need to install the dependencies once. To see all installed modules:

```
pip list
```

You can then run the scheduler through the main script:

```
python3 clock.py
```

## Deployment

The application can be deployed on a server to ensure that it is executed at a specific interval. Heroku clock processes was used for my deployment. 
More info can be found [here](https://devcenter.heroku.com/articles/clock-processes-python).
