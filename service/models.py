"""
Models for Promotion

All of the models are stored in this module
"""
from datetime import datetime
import logging
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
import dateutil.parser

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

def init_db(app):
    """Initialies the SQLAlchemy app"""
    PromotionModel.init_db(app)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


# Different kinds of promotions
class TypeOfPromo(Enum):
    """Enumeration of valid Promotions's type"""
    Discount = 0 # xxx percent off
    BOGOF = 1 # Buy xxx get one free
    Unknown = 3


class PromotionModel(db.Model):
    """
    Class that represents a Promotion
    """
    
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(63), nullable=False)
    category = db.Column(
        db.Enum(TypeOfPromo), nullable=False, server_default=(TypeOfPromo.Unknown.name)
    )
    product_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False) # xxx percent off, or Byu xxx get one free
    description = db.Column(db.String(63), nullable=True)
    from_date = db.Column(db.DateTime(), nullable=False)
    to_date = db.Column(db.DateTime(), nullable=False)
    

    def __repr__(self):
        return "<Promotion for %r id=[%s]>" % (self.product_name, self.id)

    def create(self):
        """
        Creates a Promotion to the database
        """
        logger.info("Creating Promotion for %s", self.product_name)
        self.id = None  # id must be none to generate next primary key
        if self.category == TypeOfPromo.Discount and self.amount > 100:
            raise DataValidationError("Discount cannot exceed 100%")
        if self.amount <= 0:
            raise DataValidationError("amount must be grater than 0")
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Saving Promotion for %s", self.product_name)
        db.session.commit()

    def delete(self):
        """ Removes a Promotion from the data store """
        logger.info("Deleting Promotion for %s", self.product_name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        return {
            "id": self.id,
            "product_name": self.product_name,
            "category": self.category.name,
            "product_id": self.product_id,
            "amount": self.amount,
            "description": self.description,
            "from_date": self.from_date.isoformat(),
            "to_date": self.to_date.isoformat(),
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_name = data["product_name"]
            self.category = getattr(TypeOfPromo, data["category"])
            self.product_id = data['product_id']
            self.amount = data["amount"]
            self.description = data["description"]
            self.from_date = data["from_date"]
            self.to_date = data["to_date"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Promotions in the database """
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, by_id:int):
        """ Finds a Promotion by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id:int):
        """ Find a Promotion by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_product_name(cls, product_name:str) -> list:
        """Returns all Promotions with the given name

        Args:
            name (string): the name of the Promotions you want to match
        """
        logger.info("Processing product query for name=%s ...", product_name)
        return cls.query.filter(cls.product_name == product_name)

    @classmethod
    def find_by_category(cls, category:TypeOfPromo=TypeOfPromo.Unknown) -> list:
        """Returns all of the Pets in a category

        :param category: the category of the Pets you want to match
        :type category: str

        :return: a collection of Pets in that category
        :rtype: list

        """
        logger.info("Processing category query for %s ...", category.name)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_product_id(cls, product_id:int) -> list:
        """Returns all Promotions with the product id

        Args:
            product_id (int): the product of the Promotions you want to match
        """ 
        logger.info("Processing product query for id=%s ...", product_id)
        return cls.query.filter(cls.product_id == product_id)
    
    @classmethod
    def find_by_from_date(cls, from_date:str) -> list:
        """Returns all Promotions with the from date

        Args:
            from_date (str): the start date of the Promotions you want to match
        """ 
        logger.info("Processing start date query for %s ...", from_date)
        return cls.query.filter(cls.from_date == dateutil.parser.parse(from_date))

    @classmethod
    def find_by_to_date(cls, to_date:str) -> list:
        """Returns all Promotions with the to date

        Args:
            to_date (str): the end date of the Promotions you want to match
        """ 
        logger.info("Processing end date query for %s ...", to_date)
        return cls.query.filter(cls.to_date == dateutil.parser.parse(to_date))

    @classmethod
    def find_by_availability(cls, available:bool=True) -> list:
        """Returns all Pets by their availability

        :param available: True for pets that are available
        :type available: str

        :return: a collection of Pets that are available
        :rtype: list

        """
        logger.info("Processing available query for %s ...", available)
        if available:
            return cls.query.filter(
                cls.from_date <= datetime.now()).filter(
                    cls.to_date >= datetime.now()
                )
        else:
            return cls.query.filter(
                (cls.from_date > datetime.now()) | (datetime.now() > cls.to_date)
            )

    @classmethod
    def find_best_promotion_for_product(cls, product_id:int):
        promotions = cls.query.filter(
            cls.product_id == product_id
            ).filter(
            cls.from_date <= datetime.now()).filter(
                cls.to_date >= datetime.now()
            )
        promotion_list = [promotion for promotion in promotions]
        max_off = 0
        best_promotion = None
        for promotion in promotion_list:
            if promotion.category == TypeOfPromo.Discount:
                off = promotion.amount / 100.
            elif promotion.category == TypeOfPromo.BOGOF:
                off = 1. / promotion.amount
            if off > max_off:
                max_off = off
                best_promotion = promotion
        return best_promotion