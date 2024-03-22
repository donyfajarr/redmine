import mysql.connector

def my_cron_job():    
    try:
        connection = mysql.connector.connect(
            host='10.58.1.2',
            port='3307',
            database='bitnami_redmine',
            user='report',
            password='mokondo12'
        )
        if connection.is_connected():
            print('Connected to MySQL database')

        # Create a cursor object
        cursor = connection.cursor()

        # Define the SQL query
        # query = "SELECT * FROM "
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema='bitnami_redmine'"
        # query = "SELECT user_id, address FROM email_addresses"
        # query = "SELECT column_name FROM information_schema.columns WHERE table_schema='bitnami_redmine' AND table_name = 'email_addresses'"
        # query = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"

        # Execute the query
        cursor.execute(query)

        # Fetch all the rows
        rows = cursor.fetchall()

        # Process the rows
        for row in rows:
            print(row)
            # id, email = row
            # print(id)
        # try:
        #     models = models.user.objects.get(id=)

    except mysql.connector.Error as e:
        print(f'Error connecting to MySQL database: {e}')

    finally:
        # Close cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print('Connection to MySQL database closed')