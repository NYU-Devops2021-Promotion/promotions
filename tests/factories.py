"""
Test Factory to make fake objects for testing
"""
from datetime import datetime, timedelta
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Promotion, TypeOfPromo, StatusOfPromo


class PromotionFactory(factory.Factory):
    """Creates fake promotions that you don't have to feed"""

    class Meta:
        model = Promotion

    id = factory.Sequence(lambda n: n)
    product_name = factory.LazyAttribute(lambda o: 'iphone%s' % o.id)
    category = FuzzyChoice(choices=[TypeOfPromo.Discount, TypeOfPromo.BOGOF, TypeOfPromo.Unknown])
    status = FuzzyChoice(choices=[StatusOfPromo.Used, StatusOfPromo.Unused])

    product_id = factory.Sequence(lambda n: n)
    amount = FuzzyChoice(choices=[5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
    description = "description"
    from_date = factory.Sequence(lambda n: datetime.now() + timedelta(days = n - 20))
    to_date = factory.Sequence(lambda n: datetime.now() + timedelta(days = n - 13))