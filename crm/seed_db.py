import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")  # ⚠️ replace with your project name
django.setup()

from crm.models import Customer, Product, Order


def seed_customers():
    customers_data = [
        {"name": "Alice", "email": "alice@example.com", "phone": "12345"},
        {"name": "Bob", "email": "bob@example.com", "phone": "67890"},
        {"name": "Charlie", "email": "charlie@example.com", "phone": "11223"},
    ]

    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data["email"],
            defaults={"name": data["name"], "phone": data["phone"]}
        )
        if created:
            print(f"Created customer: {customer.name}")
        else:
            print(f"Customer already exists: {customer.name}")


def seed_products():
    products_data = [
        {"name": "Laptop", "price": Decimal("850.00"), "stock": 10},
        {"name": "Phone", "price": Decimal("500.00"), "stock": 20},
        {"name": "Headphones", "price": Decimal("75.00"), "stock": 50},
    ]

    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data["name"],
            defaults={"price": data["price"], "stock": data["stock"]}
        )
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")


def seed_orders():
    if not Customer.objects.exists() or not Product.objects.exists():
        print("Cannot create orders: customers or products missing.")
        return

    customer = Customer.objects.first()
    products = Product.objects.all()[:2]  # first 2 products
    order = Order.objects.create(customer=customer, total_amount=0)
    order.products.set(products)
    order.total_amount = sum([p.price for p in products])
    order.save()
    print(f"created order for {customer.name} with {len(products)} products.")


def run():
    print("Seeding database...")
    seed_customers()
    seed_products()
    seed_orders()
    print("Done seeding!")


if __name__ == "__main__":
    run()
