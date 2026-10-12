from .base import BaseAdapter
from .flipkart import FlipkartAdapter
from .amazon import AmazonAdapter
from .registry import REGISTRY, AdapterRegistry

__all__ = ["BaseAdapter", "FlipkartAdapter", "AmazonAdapter", "REGISTRY", "AdapterRegistry"]
