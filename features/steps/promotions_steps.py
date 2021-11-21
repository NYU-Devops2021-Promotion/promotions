import json
import requests
from behave import given
from compare import expect

@given('the following promotions')
def step_impl(context):
    """ Delete all Promotions and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the pets and delete them one by one
    context.resp = requests.get(context.base_url + '/promotions', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for promotion in context.resp.json():
        context.resp = requests.delete(context.base_url + '/promotions/' + str(promotion["_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new pets
    create_url = context.base_url + '/promotions'
    for row in context.table:
        data = {
            "product_name": row['product_name'],
            "category": row['category'],
            "product_id": int(row['product_id']),
            "amount": int(row['amount']),
            "description": "Great Deal",
            "from_date": row['from_date'],
            "to_date": row['to_date']
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)