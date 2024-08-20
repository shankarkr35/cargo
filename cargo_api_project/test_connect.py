from django.db import connection

try:
    # Execute a simple query to check the database connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")

    # If the query executed successfully, the connection is established
    print("Database connection is established.")

except Exception as e:
    # If an exception occurs, the connection is not established
    print("Database connection is not established:", str(e))
