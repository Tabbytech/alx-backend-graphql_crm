import requests  # <-- add this
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    # Configure GraphQL client
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL query to fetch metrics
    query = gql("""
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """)

    result = client.execute(query)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"{timestamp} - Report: {result['totalCustomers']} customers, {result['totalOrders']} orders, {result['totalRevenue']} revenue\n"

    with open("/tmp/crm_report_log.txt", "a") as f:
        f.write(report)
    
    print("CRM report generated!")
