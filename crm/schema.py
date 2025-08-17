import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from crm.models import Customer, Product, Order


# ==============================
# GraphQL Types
# ==============================
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ==============================
# Mutations
# ==============================

# 1. Create a single customer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # Validate unique email
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")

        # Validate phone format if provided
        if phone and not re.match(r"^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$", phone):
            raise ValidationError("Invalid phone format.")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully!")


# 2. Bulk create customers
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(
            graphene.JSONString, required=True
        )  # Expect list of dicts {name, email, phone}

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, customers):
        created_customers = []
        errors = []

        for customer_data in customers:
            try:
                name = customer_data.get("name")
                email = customer_data.get("email")
                phone = customer_data.get("phone")

                if not name or not email:
                    raise ValidationError("Name and Email are required.")

                if Customer.objects.filter(email=email).exists():
                    raise ValidationError(f"Email already exists: {email}")

                if phone and not re.match(r"^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$", phone):
                    raise ValidationError(f"Invalid phone format for: {phone}")

                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                created_customers.append(customer)

            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# 3. Create product
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise ValidationError("Price must be positive.")
        if stock < 0:
            raise ValidationError("Stock cannot be negative.")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


# 4. Create order
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID.")

        if not product_ids:
            raise ValidationError("At least one product must be selected.")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise ValidationError("Some product IDs are invalid.")

        order = Order.objects.create(customer=customer)
        order.products.set(products)

        total_amount = sum([p.price for p in products])
        order.total_amount = total_amount
        order.save()

        return CreateOrder(order=order)


# ==============================
# Query + Mutation Root
# ==============================
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

