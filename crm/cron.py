from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Logs a heartbeat every 5 minutes and optionally queries GraphQL hello."""
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{now} CRM is alive"

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    try:
        query = gql("{ hello }")
        result = client.execute(query)
        if "hello" in result:
            message += " (GraphQL responsive)"
        else:
            message += " (GraphQL failed)"
    except Exception as e:
        message += f" (GraphQL error: {e})"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message + "\n")


def update_low_stock():
    """Calls GraphQL mutation to restock products with stock < 10 and logs updates"""
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_msg = f"{now} UpdateLowStockProducts: "

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    mutation = gql("""
    mutation {
        updateLowStockProducts {
            message
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """)

    try:
        result = client.execute(mutation)
        data = result.get("updateLowStockProducts", {})
        log_msg += data.get("message", "No message returned")
        for p in data.get("updatedProducts", []):
            log_msg += f"\n   - {p['name']} → stock: {p['stock']}"
    except Exception as e:
        log_msg += f"Request error: {str(e)}"

    with open("/tmp/low_stock_updates_log.txt", "a") as f:
        f.write(log_msg + "\n")
