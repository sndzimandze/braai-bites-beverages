"""
Database Models
"""
from datetime import datetime
from extensions import db


class Product(db.Model):
    """Product model for storing product information"""

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    image = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.id}: {self.title}>'

    @property
    def in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0

    @property
    def formatted_price(self):
        """Return formatted price with currency"""
        return f"R {self.price:.2f}"

    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'image': self.image,
            'price': self.price,
            'formatted_price': self.formatted_price,
            'stock': self.stock,
            'in_stock': self.in_stock,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
