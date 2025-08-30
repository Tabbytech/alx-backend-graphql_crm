#!/bin/bash
# Script to clean up inactive customers (no orders in the past year)

# Navigate to project root
cd "$(dirname "$0")/../.."

# Run Django shell command to delete inactive customers
deleted_count=$(python3 manage.py shell -c "
from django.utils import timezone
from crm.models import Customer, Order
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=365)

# Customers with orders in the last year
active_customers = Customer.objects.filter(order__order_date__gte=cutoff).distinct()

# Inactive customers = all customers except active ones
inactive_customers = Customer.objects.exclude(id__in=active_customers)

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log result with timestamp
echo \"$(date '+%Y-%m-%d %H:%M:%S') Deleted inactive customers: $deleted_count\" >> /tmp/customer_cleanup_log.txt
