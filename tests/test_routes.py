"""
TestPromotion API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
import json

from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import status  # HTTP Status Codes
from service.models import db, Promotion, TypeOfPromo
from service.routes import app, init_db
from urllib.parse import quote_plus
from .factories import PromotionFactory
from datetime import datetime, timedelta


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']
BASE_API = "/api/promotions"
CONTENT_TYPE_JSON = "application/json"
######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################
    def _create_promotions(self, count):
        """Factory method to create promotion in bulk"""
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            resp = self.app.post(
                BASE_API, json=test_promotion.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
            new_promotion = resp.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_promotion(self):
        """Get a single Promotion"""
        # get the id of a promotio
        test_promotion = self._create_promotions(1)[0]
        resp = self.app.get(
            BASE_API + "/{}".format(test_promotion.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_name"], test_promotion.product_name)
    
    def test_get_promotion_not_found(self):
        """Get a Promotion thats not found"""
        resp = self.app.get("/promotions/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_promotion_list(self):
        """Get a list of promotions"""
        self._create_promotions(5)
        resp = self.app.get(BASE_API)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)
            
    def test_method_not_allowed(self):
        """Get a http request thats not allowed"""
        resp = self.app.post("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_promotion_no_content_type(self):
         """Create a promotion with no content type"""
         resp = self.app.post(BASE_API)
         self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_best_promotion(self):
        """Get the best promotion for a product"""
        current_date = datetime.now()
        resp = self.app.get(
            "/promotions/{}/best".format(11111), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        promotions = []
        promotions.append(Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
        ))
        promotions.append(Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=20, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
        ))
        promotions.append(Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=30, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 7), 
            to_date=datetime(2021, 10, 13)
        ))# invalid promotion
        promotions.append(Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.BOGOF, 
            product_id=11111, amount=6, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
        ))
        for promotion in promotions:
            resp = self.app.post(
                BASE_API, json=promotion.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
        resp = self.app.get(BASE_API + "/11111/best", content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        app.logger.info(data)
        self.assertEqual(data["category"], TypeOfPromo.Discount.name)
        self.assertEqual(data["product_name"], "Macbook")
        self.assertEqual(data["product_id"], 11111)
        self.assertEqual(data["amount"], 20)
        self.assertEqual(data["description"], "Gread Deal")
        self.assertEqual(data["from_date"], (current_date - timedelta(days=1)).isoformat())
        self.assertEqual(data["to_date"], (current_date + timedelta(days=5)).isoformat())

        # Not found
        resp = self.app.get(BASE_API + "/11112/best", content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    # Test quey promotion list
    ######################################################################

    def test_query_promotion_list_by_category(self):
        """Query promotions by Category"""
        promotions = self._create_promotions(10)
        test_category = promotions[0].category

        category_promotions = [promotion for promotion in promotions if promotion.category == test_category]
        logging.debug(promotions[0])
        resp = self.app.get(
            BASE_API, query_string="category={}".format((test_category))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["category"], test_category.name)
            
    def test_query_promotion_list_by_product_name(self):
        """Query promotions by Product Name"""
        promotions = self._create_promotions(10)
        test_name = promotions[0].product_name

        name_promotions = [promotion for promotion in promotions if promotion.product_name == test_name]
        logging.debug(promotions[0])
        resp = self.app.get(
            BASE_API, query_string="product_name={}".format((test_name))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["product_name"], test_name)

    def test_query_promotion_list_by_product_id(self):
        """Query promotions by Product ID"""
        promotions = self._create_promotions(10)
        test_product_id= promotions[0].product_id

        product_id_promotions = [promotion for promotion in promotions if promotion.product_id == test_product_id]
        logging.debug(promotions[0])
        resp = self.app.get(
            BASE_API, query_string="product_id={}".format((test_product_id))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(product_id_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["product_id"], test_product_id)
    
    def test_query_promotion_list_by_from_date(self):
        """Query promotions by From Date"""
        promotions = self._create_promotions(10)
        test_from_date= promotions[0].from_date

        from_date_promotions = [promotion for promotion in promotions if promotion.from_date == test_from_date]
        logging.debug(promotions[0])
        resp = self.app.get(
            BASE_API, query_string="from_date={}".format((test_from_date))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(from_date_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["from_date"], test_from_date.isoformat())
    
    def test_query_promotion_list_by_to_date(self):
        """Query promotions by To Date"""
        promotions = self._create_promotions(10)
        test_to_date= promotions[0].to_date
        to_date_promotions = [promotion for promotion in promotions if promotion.to_date == test_to_date]
        logging.debug(promotions[0])
        resp = self.app.get(
            BASE_API, query_string="to_date={}".format((test_to_date))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(to_date_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["to_date"], test_to_date.isoformat())

    def test_query_promotion_list_by_availability(self):
        """Query promotions by Availability"""
        promotions = self._create_promotions(10)
        availability = 1
        availability_promotions = [promotion for promotion in promotions if promotion.is_available()]
        logging.debug(promotions[0])
        resp = self.app.get(
            BASE_API, query_string="available={}".format(availability)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(availability_promotions))
        
        availability = 0
        availability_promotions = [promotion for promotion in promotions if not promotion.is_available()]
        logging.debug(promotions[0])
        resp = self.app.get(
            BASE_API, query_string="available={}".format(availability)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(availability_promotions))

    def test_query_promotion_list_by_multiAttri(self):
        """Query promotions by more than one attributes"""
        promotions = self._create_promotions(10)
        for promotion in promotions:
            logging.debug(promotion)
            availability = 1 if promotion.is_available() else 0
            resp = self.app.get(
                BASE_API, query_string="category={}&product_name={}&product_id={}&from_date={}&to_date={}&available={}".format(
                    promotion.category, promotion.product_name, promotion.product_id, promotion.from_date, promotion.to_date, availability)
            )
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            self.assertEqual(data[0]["id"], promotion.id)
    
    
    ######################################################################
    # END
    ######################################################################
            
    def test_create_promotion(self):
        """Create a new Promotion"""
        test_promotion = PromotionFactory()
        resp = self.app.post(
            BASE_API, json=test_promotion.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_promotion = resp.get_json()
        self.assertEqual(new_promotion["amount"], test_promotion.amount, "Amount does not match")
        self.assertEqual(new_promotion["category"], test_promotion.category.name, "Categoriy does not match")
        self.assertEqual(new_promotion["description"], test_promotion.description, "Description does not match")
        self.assertEqual(new_promotion["from_date"], test_promotion.from_date.isoformat(), "From date does not match")
        self.assertEqual(new_promotion["product_id"], test_promotion.product_id, "Product id does not match")
        self.assertEqual(new_promotion["product_name"], test_promotion.product_name, "Name does not match")
        self.assertEqual(new_promotion["to_date"], test_promotion.to_date.isoformat(), "To date does not match")
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_promotion = resp.get_json()
        self.assertEqual(new_promotion["amount"], test_promotion.amount, "Amount does not match")
        self.assertEqual(new_promotion["category"], test_promotion.category.name, "Categoriy does not match")
        self.assertEqual(new_promotion["description"], test_promotion.description, "Description does not match")
        self.assertEqual(new_promotion["from_date"], test_promotion.from_date.isoformat(), "From date does not match")
        self.assertEqual(new_promotion["product_id"], test_promotion.product_id, "Product id does not match")
        self.assertEqual(new_promotion["product_name"], test_promotion.product_name, "Name does not match")
        self.assertEqual(new_promotion["to_date"], test_promotion.to_date.isoformat(), "To date does not match")

    def test_expire_promotion(self):
        """Expire an existing Promotion"""
        # create a promotion to update
        test_promotion = self._create_promotions(1)[0]

        test_promotion.from_date = datetime.now() - timedelta(days=1) 
        test_promotion.to_date = datetime.now() + timedelta(days=1) 
        self.assertEqual(test_promotion.is_available(), True)
        logging.debug(test_promotion.from_date)
        resp = self.app.put(
            BASE_API + "/{}/expire".format(test_promotion.id + 1),
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        resp = self.app.put(
            BASE_API + "/{}/expire".format(test_promotion.id),
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        test_promotion.deserialize(data)
        logging.debug(test_promotion)

        self.assertEqual(test_promotion.is_available(), False)

    def test_update_promotion(self):
        """Update an existing Promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        resp = self.app.post(
            BASE_API, json=test_promotion.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = resp.get_json()
        logging.debug(new_promotion)
        new_promotion["category"] = "Unknown"
        resp = self.app.put(
            BASE_API + "/{}".format(new_promotion["id"]),
            json=new_promotion,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_promotion = resp.get_json()
        self.assertEqual(updated_promotion["category"], "Unknown")

    def test_delete_promotion(self):
        """Delete a Promotion"""
        test_promotion = self._create_promotions(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_API, test_promotion.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_API, test_promotion.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
