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
from flask_restx import Api, Resource, fields, reqparse, inputs
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound
from datetime import datetime, timedelta
from functools import wraps
import secrets

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
    return app.send_static_file("index.html")

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Promotion Demo REST API Service',
          description='This is a sample server Pet store server.',
          default='pets',
          default_label='Promotion operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
          #authorizations=authorizations,
          prefix='/api'
         )


# Define the model so that the docs reflect what can be sent
create_model = api.model('Promotion', {
    "product_name": fields.String(required=True,
                          description='The name of the product this promotion is for'),
    "category": fields.String(required=True,
                              description='The category of Promotion (e.g., Discount, BOGOF, etc.)'),
    "product_id": fields.Integer(required=True,
                              description='The id of the product this promotion is for'),
    "amount": fields.Integer(required=True,
                              description='The value of the Promotion (e.g., 25 percent off, buy 1 get one free, etc.)'),
    "description": fields.String(required=True,
                              description='The description of the promotion'),
    "from_date": fields.String(required=True,
                                description='The start date of the promotion (e.g., 2021-11-28)'),
    "to_date": fields.String(required=True,
                                description='The end date of the promotion (e.g., 2021-12-28)')
})

promotion_model = api.inherit(
    'PromotionModel', 
    create_model,
    {
        'id': fields.Integer(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)


# query string arguments
pro_args = reqparse.RequestParser()
pro_args.add_argument('product_name', type=str, required=False, help='List Promotions by product name')
pro_args.add_argument('product_id', type=int, required=False, help='List Promotions by product id')
pro_args.add_argument('category', type=str, required=False, help='List Promotions by category')
pro_args.add_argument('from_date', type=str, required=False, help='List Promotions by start date')
pro_args.add_argument('to_date', type=str, required=False, help='List Promotions by end date')
pro_args.add_argument('available', type=int, required=False, help='List Promotions by availability, (e.g. 1=available, 0=not_available')

######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

######################################################################
#  PATH: /promotions/{id}
######################################################################
@api.route('/promotions/<promotion_id>')
@api.param('promotion_id', 'The Promotion identifier')
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the manipulation of a single Promotion
    GET /promotion{id} - Returns a Promotion with the id
    PUT /promotion{id} - Update a Promotion with the id
    DELETE /promotion{id} -  Deletes a Promotion with the id
    """
    #------------------------------------------------------------------
    # RETRIEVE A PET
    #------------------------------------------------------------------
    @api.doc('get_promotions')
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single promotion

        This endpoint will return a promotion based on it's id
        """
        app.logger.info("Request for promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found.".format(promotion_id))

        app.logger.info("Returning promotion: %s", promotion.product_name)
        return promotion.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PET
    #------------------------------------------------------------------
    @api.doc('update_pets')
    @api.response(404, 'Pet not found')
    @api.response(400, 'The posted Pet data was not valid')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info("Request to update promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        promotion.deserialize(api.payload)
        promotion.id = promotion_id
        promotion.update()

        app.logger.info("Promotion with ID [%s] updated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A PET
    #------------------------------------------------------------------
    @api.doc('delete_pets')
    @api.response(204, 'Pet deleted')
    def delete(self, promotion_id):
        """
        Delete a promotion
        This endpoint will delete a promotion based the id specified in the path
        """
        app.logger.info("Request to delete promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
        app.logger.info("Promotion with ID [%s] delete complete.", promotion_id)
        return '', status.HTTP_204_NO_CONTENT



######################################################################
# PATH: /promotions
######################################################################
@api.route('/promotions', strict_slashes=False)
class PromotionCollection(Resource):
    """ Handles all interactions with collections of Pets """
    #------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    #------------------------------------------------------------------
    @api.doc('list_promotions')
    @api.expect(pro_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """Returns all of the promotions"""
        app.logger.info("Request for promotion list")
        promotions = []
        args = pro_args.parse_args()
        app.logger.info('Filtering list')
        promotions = Promotion.find_by_multi_attributes(args)

        results = [promotion.serialize() for promotion in promotions]
        app.logger.info("Returning %d promotions", len(results))
        app.logger.info((results))

        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # ADD A NEW PROMOTION
    #------------------------------------------------------------------
    @api.doc('create_promotions')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(promotion_model, code=201)
    def post(self):
        """
        Creates a Promotion
        This endpoint will create a Promotion based the data in the body that is posted
        """
        app.logger.info("Request to create a promotion")
        promotion = Promotion()
        logging.debug('Payload = %s', api.payload)
        promotion.deserialize(api.payload)
        promotion.create()
        location_url = api.url_for(PromotionResource, promotion_id=promotion.id, _external=True)

        logging.info("Promotion with ID [%s] created.", promotion.id)
        return promotion.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
# PATH: /promotions/{id}/expire
######################################################################
@api.route("/promotions/<promotion_id>/expire")
@api.param('promotion_id', 'The promotion identifier')
class ExpireResource(Resource):
    """Expire actions on a promotion"""
    @api.doc('expire_promotions')
    @api.response(404, 'Pet not found')
    def put(self, promotion_id):
        """
        Set a Promotion to expired

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info("Request to expire promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        
        if not promotion:
            abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found.".format(promotion_id))

        # Set the to-date to 1 day before from-date
        promotion.to_date = promotion.from_date-timedelta(days=1) 
        promotion.update()

        app.logger.info("Promotion with ID [%s] expired.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

######################################################################
# FIND THE BEST PROMOTION FOR A PRODUCT
######################################################################
@api.route("/promotions/<product_id>/best")
@api.param('product_id', 'The product identifier')
class BestResource(Resource):
    """Get Best Promotion actions on a product"""
    @api.doc('find_best_promotions')
    @api.response(404, 'Promotion not found')
    def get(self, product_id):
        """
        Get the best promotion for a product
        This endpoint will get the best promotion based the product's id specified in the path
        """
        app.logger.info("Request to get the best promotion with product: %s", product_id)
        promotion = Promotion.find_best_promotion_for_product(int(product_id))

        if not promotion:
            abort(status.HTTP_404_NOT_FOUND, "Promotion with product id '{}' was not found.".format(product_id))

        app.logger.info("Returning best promotion: %s", promotion.product_name)
        return promotion.serialize(), status.HTTP_200_OK

    

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)

@app.before_first_request
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Promotion.init_db(app)