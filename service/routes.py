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


# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import PromotionModel, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )

    
######################################################################
# LIST ALL promotionS
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the promotions"""
    app.logger.info("Request for promotion list")
    promotions = []
    category = request.args.get("category")
    name = request.args.get("product_name")
    if category:
        app.logger.info("Category: %s", category)
        promotions = PromotionModel.find_by_category(category)
    elif name:

        promotions = PromotionModel.find_by_product_name(name)
    else:
        promotions = PromotionModel.all()

    results = [promotion.serialize() for promotion in promotions]
    app.logger.info("Returning %d promotions", len(results))
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
    promotion = PromotionModel.find(promotion_id)
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
    promotion = PromotionModel()
    promotion.deserialize(request.get_json())
    promotion.create()
    message = promotion.serialize()
    location_url = url_for("get_promotions", promotion_id=promotion.id, _external=True)

    app.logger.info("Promotion with ID [%s] created.", promotion.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )



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
    promotion = PromotionModel.find(promotion_id)
    if promotion:
        promotion.delete()
    app.logger.info("Promotion with ID [%s] delete complete.", promotion_id)
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    PromotionModel.init_db(app)
