from .base import BaseCategory, MetricDefinition
from .smartphones import SmartphoneCategory
from .laptops import LaptopCategory

CATEGORIES = {
    "smartphones": SmartphoneCategory,
    "laptops": LaptopCategory
}

def get_category(category_id: str = "smartphones"):
    return CATEGORIES.get(category_id, SmartphoneCategory)
