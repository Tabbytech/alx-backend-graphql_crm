#!/usr/bin/env python3
"""
Send order reminders for orders created within the last 7 days.
Logs order ID and customer email to /tmp/order_reminders_log.txt
"""

from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# GraphQL query
query = gql("""
query RecentOrders($cutoff: DateTime!) {
  orders(orderDate_Gte: $cutoff) {
    id
    customer {
      email
    }
  }
}
""")

cutoff = (datetime.now() - timedelta(days=7)).isoformat()
result = client.execute(query, variable_values={"cutoff": cutoff})

orders = result.get("orders", [])
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open("/tmp/order_reminders_log.txt", "a") as f:
    for order in orders:
        f.write(f"{timestamp} Order {order['id']} -> {order['customer']['email']}\n")

print("Order reminders processed!")
