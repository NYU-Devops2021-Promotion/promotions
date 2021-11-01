"""
Test cases for Promotion Model

"""
import logging
import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Promotion, TypeOfPromo, DataValidationError, db
from service import app
from .factories import PromotionFactory
from datetime import datetime, timedelta

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  <your resource name>   M O D E L   T E S T   C A S E S
######################################################################
class TestPromotion(unittest.TestCase):
    """ Test Cases for Promotion Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_promotion(self):
        """Create a promotion and assert that it exists"""
        promotion = Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            )
        self.assertTrue(promotion != None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.product_name, "Macbook")
        self.assertEqual(promotion.category, TypeOfPromo.Discount)
        self.assertEqual(promotion.product_id, 11111)
        self.assertEqual(promotion.amount, 10)
        self.assertEqual(promotion.description, "Gread Deal")
        self.assertEqual(promotion.from_date, datetime(2021, 10, 13))
        self.assertEqual(promotion.to_date, datetime(2021, 10, 19))
        promotion = Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.BOGOF, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            )
        self.assertEqual(promotion.category, TypeOfPromo.BOGOF)
        promotion = Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Unknown, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            )
        self.assertEqual(promotion.category, TypeOfPromo.Unknown)

    def test_add_a_promotion(self):
        """Create a promotion and add it to the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=-1, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            )
        self.assertTrue(promotion != None)
        self.assertEqual(promotion.id, None)
        self.assertRaises(DataValidationError, promotion.create)
        promotion.amount = 101
        self.assertRaises(DataValidationError, promotion.create)
        promotion.amount = 10
        promotion.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(promotion.id, 1)
        promotions = promotion.all()
        self.assertEqual(len(promotions), 1)

    def test_update_a_promotion(self):
        """Update a promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.create()
        logging.debug(promotion)
        self.assertEqual(promotion.id, 1)
        # Change it an save it
        promotion.amount = 15
        original_id = promotion.id
        promotion.update()
        self.assertEqual(promotion.id, original_id)
        self.assertEqual(promotion.amount, 15)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].id, 1)
        self.assertEqual(promotions[0].amount, 15)

    def test_delete_a_promotion(self):
        """Delete a promotion"""
        promotion = PromotionFactory()
        promotion.create()
        self.assertEqual(len(promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(promotion.all()), 0)

    def test_serialize_a_promotion(self):
        """Test serialization of a promotion"""
        promotion = PromotionFactory()
        data = promotion.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], promotion.id)
        self.assertIn("product_name", data)
        self.assertEqual(data["product_name"], promotion.product_name)
        self.assertIn("category", data)
        self.assertEqual(data["category"], promotion.category.name)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], promotion.product_id)
        self.assertIn("amount", data)
        self.assertEqual(data["amount"], promotion.amount)
        self.assertIn("description", data)
        self.assertEqual(data["description"], promotion.description)
        self.assertIn("from_date", data)
        self.assertEqual(data["from_date"], promotion.from_date.isoformat())
        self.assertIn("to_date", data)
        self.assertEqual(data["to_date"], promotion.to_date.isoformat())




    def test_deserialize_a_promotion(self):
        """Test deserialization of a promotion"""
        data = {
            "id": 1,
            "product_name": "iwatch",
            "category": "Discount",
            "product_id": 100,
            "amount": 10,
            "description": "Great Deal",
            "from_date": datetime(2021, 10, 13),
            "to_date": datetime(2021, 10, 19),
        }
        promotion = Promotion()
        promotion.deserialize(data)
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.product_name, "iwatch")
        self.assertEqual(promotion.category, TypeOfPromo.Discount)
        self.assertEqual(promotion.product_id, 100)
        self.assertEqual(promotion.amount, 10)
        self.assertEqual(promotion.description, "Great Deal")
        self.assertEqual(promotion.from_date, datetime(2021, 10, 13))
        self.assertEqual(promotion.to_date, datetime(2021, 10, 19))

    def test_deserialize_missing_data(self):
        """Test deserialization of a promotion with missing data"""
        data = {
            "id": 1,
            "product_name": "iwatch",
            "category": "Discount",
            "product_id": 100,
            "amount": 10,
            "description": "Great Deal",
            "from_date": datetime(2021, 10, 13),
        }
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_attribute(self):
        """ Test deserialization of bad gender attribute """
        test_promotion = PromotionFactory()
        data = test_promotion.serialize()
        data["category"] = "discount" # wrong case
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_find_promotion(self):
        """Find a promotion by ID"""
        promotions = PromotionFactory.create_batch(3)
        for promotion in promotions:
            promotion.create()
        logging.debug(promotions)
        # make sure they got saved
        self.assertEqual(len(promotion.all()), 3)
        # find the 2nd promotion in the list
        promotion = Promotion.find(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.product_name, promotions[1].product_name)
        self.assertEqual(promotion.category, promotions[1].category)
        self.assertEqual(promotion.product_id, promotions[1].product_id)
        self.assertEqual(promotion.amount, promotions[1].amount)
        self.assertEqual(promotion.description, promotions[1].description)
        self.assertEqual(promotion.from_date, promotions[1].from_date)
        self.assertEqual(promotion.to_date, promotions[1].to_date)

    def test_find_or_404_found(self):
        """Find or return 404 found"""
        promotions = PromotionFactory.create_batch(3)
        for promotion in promotions:
            promotion.create()

        promotion = promotion.find_or_404(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.product_name, promotions[1].product_name)
        self.assertEqual(promotion.category, promotions[1].category)
        self.assertEqual(promotion.product_id, promotions[1].product_id)
        self.assertEqual(promotion.amount, promotions[1].amount)
        self.assertEqual(promotion.description, promotions[1].description)
        self.assertEqual(promotion.from_date, promotions[1].from_date)
        self.assertEqual(promotion.to_date, promotions[1].to_date)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, Promotion.find_or_404, 0)

    def test_find_by_product_name(self):
        """Find a promotion by Product Name"""
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            ).create()
        Promotion(
            product_name="iwatch", 
            category=TypeOfPromo.Discount, 
            product_id=11112, amount=20, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 14), 
            to_date=datetime(2021, 10, 20)
            ).create()
        promotions = Promotion.find_by_product_name("Macbook")
        self.assertEqual(promotions[0].category, TypeOfPromo.Discount)
        self.assertEqual(promotions[0].product_name, "Macbook")
        self.assertEqual(promotions[0].product_id, 11111)
        self.assertEqual(promotions[0].amount, 10)
        self.assertEqual(promotions[0].description, "Gread Deal")
        self.assertEqual(promotions[0].from_date, datetime(2021, 10, 13)) 
        self.assertEqual(promotions[0].to_date, datetime(2021, 10, 19)) 

    def test_find_by_category(self):
        """Find promotions by Category"""
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            ).create()
        Promotion(
            product_name="iwatch", 
            category=TypeOfPromo.BOGOF, 
            product_id=11112, amount=20, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 14), 
            to_date=datetime(2021, 10, 20)
            ).create()
        promotions = Promotion.find_by_category("TypeOfPromo.BOGOF")
        self.assertEqual(promotions[0].category, TypeOfPromo.BOGOF)
        self.assertEqual(promotions[0].product_name, "iwatch")
        self.assertEqual(promotions[0].product_id, 11112)
        self.assertEqual(promotions[0].amount, 20)
        self.assertEqual(promotions[0].description, "Gread Deal")
        self.assertEqual(promotions[0].from_date, datetime(2021, 10, 14)) 
        self.assertEqual(promotions[0].to_date, datetime(2021, 10, 20))

    def test_find_by_product_id(self):
        """Find promotions by product id"""
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            ).create()
        Promotion(
            product_name="iwatch", 
            category=TypeOfPromo.BOGOF, 
            product_id=11112, amount=20, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 14), 
            to_date=datetime(2021, 10, 20)
            ).create()
        promotions = Promotion.find_by_product_id(11112)
        self.assertEqual(promotions[0].category, TypeOfPromo.BOGOF)
        self.assertEqual(promotions[0].product_name, "iwatch")
        self.assertEqual(promotions[0].product_id, 11112)
        self.assertEqual(promotions[0].amount, 20)
        self.assertEqual(promotions[0].description, "Gread Deal")
        self.assertEqual(promotions[0].from_date, datetime(2021, 10, 14)) 
        self.assertEqual(promotions[0].to_date, datetime(2021, 10, 20))

    def test_find_by_from_date(self):
        """Find promotions by start date"""
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            ).create()
        Promotion(
            product_name="iwatch", 
            category=TypeOfPromo.BOGOF, 
            product_id=11112, amount=20, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 14), 
            to_date=datetime(2021, 10, 20)
            ).create()
        promotions = Promotion.find_by_from_date("2021/10/14")
        self.assertEqual(promotions[0].category, TypeOfPromo.BOGOF)
        self.assertEqual(promotions[0].product_name, "iwatch")
        self.assertEqual(promotions[0].product_id, 11112)
        self.assertEqual(promotions[0].amount, 20)
        self.assertEqual(promotions[0].description, "Gread Deal")
        self.assertEqual(promotions[0].from_date, datetime(2021, 10, 14)) 
        self.assertEqual(promotions[0].to_date, datetime(2021, 10, 20))

    def test_find_by_to_date(self):
        """Find promotions by end date"""
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 13), 
            to_date=datetime(2021, 10, 19)
            ).create()
        Promotion(
            product_name="iwatch", 
            category=TypeOfPromo.BOGOF, 
            product_id=11112, amount=20, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 14), 
            to_date=datetime(2021, 10, 20)
            ).create()
        promotions = Promotion.find_by_to_date("2021/10/20")
        self.assertEqual(promotions[0].category, TypeOfPromo.BOGOF)
        self.assertEqual(promotions[0].product_name, "iwatch")
        self.assertEqual(promotions[0].product_id, 11112)
        self.assertEqual(promotions[0].amount, 20)
        self.assertEqual(promotions[0].description, "Gread Deal")
        self.assertEqual(promotions[0].from_date, datetime(2021, 10, 14)) 
        self.assertEqual(promotions[0].to_date, datetime(2021, 10, 20))

    def test_find_by_availability(self):
        """Find promotions by Availability"""
        current_date = datetime.now()
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
            ).create()
        Promotion(
            product_name="iwatch", 
            category=TypeOfPromo.BOGOF, 
            product_id=11112, amount=20, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 7), 
            to_date=datetime(2021, 10, 13)
            ).create()
        Promotion(
            product_name="iphone", 
            category=TypeOfPromo.BOGOF, 
            product_id=11113, amount=30, 
            description="Gread Deal", 
            from_date=current_date + timedelta(days=1), 
            to_date=current_date + timedelta(days=7)
            ).create() 
        promotions = Promotion.find_by_availability(True)
        promotion_list = [promotion for promotion in promotions]
        self.assertEqual(len(promotion_list), 1)
        self.assertEqual(promotions[0].category, TypeOfPromo.Discount)
        self.assertEqual(promotions[0].product_name, "Macbook")
        self.assertEqual(promotions[0].product_id, 11111)
        self.assertEqual(promotions[0].amount, 10)
        self.assertEqual(promotions[0].description, "Gread Deal")
        self.assertEqual(promotions[0].from_date, current_date - timedelta(days=1)) 
        self.assertEqual(promotions[0].to_date, current_date + timedelta(days=5)) 
        promotions = Promotion.find_by_availability(False)
        promotion_list = [promotion for promotion in promotions]
        self.assertEqual(len(promotion_list), 2)

    def test_find_best_promotion(self):
        """find the best available promotion for a product"""
        current_date = datetime.now()
        best_promotion = Promotion.find_best_promotion_for_product(11111)
        self.assertEqual(best_promotion, None)
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
        ).create()
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=20, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
        ).create()
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=30, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 7), 
            to_date=datetime(2021, 10, 13)
        ).create() # invalid promotion
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.BOGOF, 
            product_id=11111, amount=6, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
        ).create()
        best_promotion = Promotion.find_best_promotion_for_product(11111)
        self.assertEqual(best_promotion.category, TypeOfPromo.Discount)
        self.assertEqual(best_promotion.product_name, "Macbook")
        self.assertEqual(best_promotion.product_id, 11111)
        self.assertEqual(best_promotion.amount, 20)
        self.assertEqual(best_promotion.description, "Gread Deal")
        self.assertEqual(best_promotion.from_date, current_date - timedelta(days=1)) 
        self.assertEqual(best_promotion.to_date, current_date + timedelta(days=5))  

    def test_find_by_multi_attributes(self):
        """find the promotions with multiple attributes"""
        current_date = datetime.now()
        Promotion(
            product_name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
            ).create()
        Promotion(
            product_name="iphone", 
            category=TypeOfPromo.BOGOF, 
            product_id=11112, amount=30, 
            description="Gread Deal", 
            from_date=current_date + timedelta(days=1), 
            to_date=current_date + timedelta(days=7)
            ).create() 
        promotions = Promotion.all()
        for promotion in promotions:
            args = {
                "category": promotion.category,
                "product_name": promotion.product_name,
                "paoduct_id": promotion.product_id,
                "from_date": promotion.from_date,
                "to_date": promotion.to_date,
                "availablility": 1 if promotion.is_available() else 0
            }
            result = Promotion.find_by_multi_attributes(args)
            self.assertEqual(promotion.id, result[0].id)

