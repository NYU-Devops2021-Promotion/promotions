"""
Promotin Store Service

Paths:
------
GET /promotions - Returns a list all of the Promotions
GET /promotions/{id} - Returns the Promotion with a given id number
POST /promotions - creates a new Promotions record in the database
PUT /promotions/{id} - updates a Promotions record in the database
DELETE /promotions/{id} - deletes a Promotions record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound
from datetime import datetime, timedelta

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Promotion, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    '''
    return (
        jsonify(
            name="Promotion REST API Service",
            version="1.0",
            paths=url_for("list_promotions", _external=True),
        ),
        status.HTTP_200_OK,
    )
    '''
    return app.send_static_file("index.html")
    
######################################################################
# LIST ALL PROMOTIONS
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the promotions"""
    app.logger.info("Request for promotion list")
    promotions = []
    category = request.args.get("category")
    name = request.args.get("product_name")
    product_id = request.args.get("product_id")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    availabile = request.args.get("available")

    args = {}
    if category is not None:
        args["category"] = category
    if name is not None:
        args["product_name"] = name
    if product_id is not None:
        args["product_id"] = product_id
    if from_date is not None:
        args["from_date"] = from_date
    if to_date is not None:
        args["to_date"] = to_date

    if availabile is not None:
        args["availability"] = availabile
    if len(args.keys()) > 0:
        promotions = Promotion.find_by_multi_attributes(args)
    else:
        promotions = Promotion.all()

    results = [promotion.serialize() for promotion in promotions]
    app.logger.info("Returning %d promotions", len(results))
    app.logger.info((results))

    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def get_promotions(promotion_id):
    """
    Retrieve a single promotion

    This endpoint will return a promotion based on it's id
    """
    app.logger.info("Request for promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))

    app.logger.info("Returning promotion: %s", promotion.product_name)
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW PROMOTION
######################################################################
@app.route("/promotions", methods=["POST"])
def create_promotions():
    """
    Creates a Promotion
    This endpoint will create a Promotion based the data in the body that is posted
    """
    app.logger.info("Request to create a promotion")
    promotion = Promotion()
    promotion.deserialize(request.get_json())
    promotion.create()
    message = promotion.serialize()
    location_url = url_for("get_promotions", promotion_id=promotion.id, _external=True)

    app.logger.info("Promotion with ID [%s] created.", promotion.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# UPDATE AN EXISTING PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotions(promotion_id):
    """
    Update a Promotion

    This endpoint will update a Promotion based the body that is posted
    """
    app.logger.info("Request to update promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    promotion.deserialize(request.get_json())
    promotion.id = promotion_id
    promotion.update()

    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING PROMOTION TO EXPIRED STATE
######################################################################
@app.route("/promotions/<int:promotion_id>/expire", methods=["PUT"])
def expire_promotions(promotion_id):
    """
    Set a Promotion to expired

    This endpoint will update a Promotion based the body that is posted
    """
    app.logger.info("Request to expire promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))

    # Set the to-date to 1 day before from-date
    promotion.to_date = promotion.from_date-timedelta(days=1) 
    promotion.update()

    app.logger.info("Promotion with ID [%s] expired.", promotion.id)
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotions(promotion_id):
    """
    Delete a promotion
    This endpoint will delete a promotion based the id specified in the path
    """
    app.logger.info("Request to delete promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if promotion:
        promotion.delete()
    app.logger.info("Promotion with ID [%s] delete complete.", promotion_id)
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# FIND THE BEST PROMOTION FOR A PRODUCT
######################################################################
@app.route("/promotions/<int:product_id>/best", methods=["GET"])
def get_best_promotion(product_id):
    """
    Get the best promotion for a product
    This endpoint will get the best promotion based the product's id specified in the path
    """
    app.logger.info("Request to get the best promotion with product: %s", product_id)
    promotion = Promotion.find_best_promotion_for_product(int(product_id))

    if not promotion:
        raise NotFound("Promotion with product id '{}' was not found.".format(product_id))

    app.logger.info("Returning best promotion: %s", promotion.product_name)
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

    

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Promotion.init_db(app)
