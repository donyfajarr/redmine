import mysql.connector
import models 
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
    cursor = connection.cursor()
    query = "SELECT users.id, users.firstname, users.lastname, , address FROM users JOIN email_addresses ON users.id = email_addresses.user_id"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        
        id, firstname, lastname, email = row
        try:
            models.user.objects.all().delete()
            models.user.objects.create(id=id,name=firstname+ ' ' +lastname, email=email)
        except:
            print('not exists')
except mysql.connector.Error as e:
    print(f'Error connecting to MySQL database: {e}')

finally:
    # Close cursor and connection
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print('Connection to MySQL database closed')