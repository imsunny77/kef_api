"""
Simple script to add dummy product data.
Run with: python add_dummy_products.py
"""

import os
import sys
import django
import random
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kef_api.settings")
django.setup()

from product_management.models import Category, Product

# Configuration
PRODUCT_COUNT = 50
CATEGORY_NAMES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports & Outdoors",
    "Books",
    "Toys & Games",
    "Health & Beauty",
    "Automotive",
]

# Product templates
PRODUCT_TEMPLATES = {
    "Electronics": [
        (
            "Smartphone",
            "High-performance smartphone with advanced features",
            299.99,
            1200.00,
        ),
        ("Laptop", "Powerful laptop for work and gaming", 599.99, 2500.00),
        ("Headphones", "Wireless noise-cancelling headphones", 79.99, 350.00),
        ("Smart Watch", "Fitness tracking smartwatch", 149.99, 400.00),
        ("Tablet", "Portable tablet for entertainment", 199.99, 800.00),
        ("Camera", "Digital camera with 4K video", 399.99, 1200.00),
        ("Speaker", "Bluetooth wireless speaker", 49.99, 200.00),
        ("Monitor", "27-inch 4K monitor", 249.99, 600.00),
    ],
    "Clothing": [
        ("T-Shirt", "Comfortable cotton t-shirt", 19.99, 49.99),
        ("Jeans", "Classic fit denim jeans", 39.99, 89.99),
        ("Sneakers", "Running shoes with cushioning", 59.99, 150.00),
        ("Jacket", "Waterproof winter jacket", 79.99, 200.00),
        ("Dress", "Elegant evening dress", 49.99, 150.00),
        ("Hat", "Stylish baseball cap", 14.99, 35.00),
        ("Socks", "Pack of 6 cotton socks", 9.99, 25.00),
        ("Belt", "Genuine leather belt", 24.99, 60.00),
    ],
    "Home & Garden": [
        ("Coffee Maker", "Programmable coffee maker", 49.99, 150.00),
        ("Plant Pot", "Ceramic decorative plant pot", 12.99, 40.00),
        ("Garden Tools Set", "Complete gardening tool set", 29.99, 80.00),
        ("Lamp", "Modern table lamp", 24.99, 70.00),
        ("Throw Pillow", "Decorative throw pillow", 15.99, 45.00),
        ("Candle Set", "Scented candle set", 19.99, 50.00),
        ("Wall Clock", "Vintage wall clock", 34.99, 90.00),
        ("Vase", "Glass decorative vase", 18.99, 55.00),
    ],
    "Sports & Outdoors": [
        ("Yoga Mat", "Non-slip yoga mat", 24.99, 60.00),
        ("Dumbbells", "Adjustable dumbbell set", 49.99, 150.00),
        ("Bicycle", "Mountain bike", 299.99, 800.00),
        ("Tent", "4-person camping tent", 79.99, 250.00),
        ("Backpack", "Hiking backpack", 39.99, 120.00),
        ("Water Bottle", "Insulated water bottle", 19.99, 50.00),
        ("Running Shoes", "Professional running shoes", 69.99, 180.00),
        ("Tennis Racket", "Professional tennis racket", 59.99, 200.00),
    ],
    "Books": [
        ("Novel", "Bestselling fiction novel", 12.99, 25.99),
        ("Cookbook", "Recipe cookbook", 19.99, 40.00),
        ("Biography", "Famous person biography", 14.99, 30.00),
        ("Textbook", "Educational textbook", 49.99, 120.00),
        ("Comic Book", "Graphic novel", 9.99, 20.00),
        ("Dictionary", "Comprehensive dictionary", 24.99, 50.00),
        ("Atlas", "World atlas", 29.99, 60.00),
        ("Poetry", "Poetry collection", 11.99, 25.00),
    ],
}


def main():
    print("Creating categories...")
    categories = []

    for category_name in CATEGORY_NAMES:
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={"description": f"Products in the {category_name} category"},
        )
        categories.append(category)
        if created:
            print(f"✓ Created category: {category_name}")
        else:
            print(f"  Category already exists: {category_name}")

    print(f"\nCreating {PRODUCT_COUNT} products...")
    created_count = 0
    variations = [
        "Pro",
        "Plus",
        "Deluxe",
        "Premium",
        "Classic",
        "Standard",
        "Elite",
        "Ultra",
    ]

    for i in range(PRODUCT_COUNT):
        # Select random category
        category = random.choice(categories)

        # Get product template
        if category.name in PRODUCT_TEMPLATES:
            templates = PRODUCT_TEMPLATES[category.name]
            base_name, description, min_price, max_price = random.choice(templates)
            # Add variation and unique number to ensure uniqueness
            variation = random.choice(variations)
            name = f"{base_name} {variation} {i + 1}"
        else:
            name = f"Product {i + 1}"
            description = f"Description for {name}"
            min_price = 10.00
            max_price = 100.00

        # Generate random price and stock
        price = Decimal(
            str(round(random.uniform(float(min_price), float(max_price)), 2))
        )
        stock_quantity = random.randint(0, 500)

        # Create product
        Product.objects.create(
            name=name,
            description=description,
            category=category,
            price=price,
            stock_quantity=stock_quantity,
        )

        created_count += 1
        if created_count % 10 == 0:
            print(f"  Created {created_count} products...")

    print(f"\n✓ Successfully created {created_count} products!")


main()
