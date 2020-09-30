from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def start_email_schedule():
    assign_and_email()

def assign_and_email():
    assign_codes_to_customers()
    email_all_customers()

def email_all_customers():
    customers = get_customers_for_email()
    for customer in customers:
        email = customer['fields']['Email']
        name = customer['fields']['Name']
        activation = customer['fields']['activationCode']
        customer_id = customer['id']

        send_email(email, name, activation)
        mark_as_mailed(customer_id)

def send_email(to_email, name, activation):
    data = {
        'name': name,
        'activation': activation
    }

    email = requests.post(
		os.environ.get('MAILGUN_DOMAIN_URL'),
		auth=("api", os.environ.get('MAILGUN_API_KEY')),
		data={"from": "MCSS <vp_external@mcss.ca>",
			"to": to_email,
			"subject": "MCSS Membership Card",
			"template": "membership-card",
			"h:X-Mailgun-Variables": json.dumps(data)
        }
    )

    if email.status_code == 200:
        print("Email sent to {}".format(to_email))
    else:
        print("Email not sent to {}".format(to_email))

# Get the number of activation codes required and assign each one to each customer
def assign_codes_to_customers():
    customers = get_customers()
    nb_customers = len(customers)

    if (nb_customers == 0):
        return "No purchases"

    if (nb_customers > 0):
        activation_codes = get_activation_codes(nb_customers)

    assert(len(activation_codes) == nb_customers)

    for i in range(len(activation_codes)):
        customer_id = customers[i]['id']
        card_number = activation_codes[i]['fields']['cardNo']
        activation_code = activation_codes[i]['fields']['activationCode']

        update_customer_record(customer_id, card_number, activation_code)

        code_id = activation_codes[i]['id']
        customer_email = customers[i]['fields']['Email']

        update_codes_record(code_id, customer_email)

def update_codes_record(code_id, customer_email):
    temp_field = {
        "fields": {
        "activationStatus": customer_email
    }}
    requests.patch( 
            "{}/{}".format(os.environ.get("ACTIVATION_CODES_URL"), code_id),json=temp_field,
            headers={"Authorization": str(os.environ.get("AIRTABLE_API_KEY"))})

def update_customer_record(customer_id, card_number, activation_code):
    temp_field = {
        "fields": {
        "cardNumber": card_number,
        "activationCode": activation_code
    }}
    requests.patch( 
            "{}/{}".format(os.environ.get("CUSTOMERS_URL"), customer_id),json=temp_field,
            headers={"Authorization": str(os.environ.get("AIRTABLE_API_KEY"))})

def get_activation_codes(number):
    codes = requests.get(
        os.environ.get("ACTIVATION_CODES_URL") + "?filterByFormula={} = ''&maxRecords={}".format("activationStatus", number),
        headers={"Authorization": str(os.environ.get("AIRTABLE_API_KEY"))}
    )

    if codes.status_code == 200:
        codes_json = codes.json()
        return codes_json["records"]

def get_customers():
    customers = requests.get(
        os.environ.get("CUSTOMERS_URL") + "?filterByFormula=AND({activationCode} = '', {emailSent} = '')",
        headers={"Authorization": str(os.environ.get("AIRTABLE_API_KEY"))}
    )
    if customers.status_code == 200:
        customers_json = customers.json()
        return customers_json["records"]

def get_customers_for_email():
    customers = requests.get(
        os.environ.get("CUSTOMERS_URL") + "?filterByFormula=AND(NOT({activationCode} = ''), {emailSent} = '')",
        headers={"Authorization": str(os.environ.get("AIRTABLE_API_KEY"))}
    )

    if customers.status_code == 200:
        customers_json = customers.json()
        return customers_json["records"]

def mark_as_mailed(customer_id):
    temp_field = {
        "fields": {
        "emailSent": "Yes",
    }}
    requests.patch( 
            "{}/{}".format(os.environ.get("CUSTOMERS_URL"), customer_id),json=temp_field,
            headers={"Authorization": str(os.environ.get("AIRTABLE_API_KEY"))})

sched.start()