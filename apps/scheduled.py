import mysql.connector
import requests
from datetime import date

def scheduled():
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
        query = [
            "SELECT issues.id, issues.subject, issues.project_id, projects.name, issues.start_date, issues.due_date, issues.author_id FROM issues JOIN projects ON issues.project_id = projects.id WHERE start_date = %s AND projects.status !=5",
            "SELECT issues.id, issues.subject, issues.project_id, projects.name, issues.start_date, issues.due_date, issues.author_id FROM issues JOIN projects ON issues.project_id = projects.id WHERE start_date <= %s AND %s <= due_date AND projects.status !=5",
            "SELECT issues.id, issues.subject, issues.project_id, projects.name, issues.start_date, issues.due_date, issues.author_id FROM issues JOIN projects ON issues.project_id = projects.id WHERE due_date = %s AND projects.status !=5",

        ]
        today_date = date.today()
        start_date = date(today_date.year, today_date.month, today_date.day)
        params_list = [
            (start_date,),
            (start_date, start_date,),
            (start_date,)
        ]
        results = []
        for queries, params in zip(query, params_list):
            cursor.execute(queries,params)
            rows=cursor.fetchall()
            results.append(rows)
        print(results)
        startselected_tasks = results[0]
        between_tasks = results[1]
        dueselected_tasks = results[2]
        
        startselected_tasks = [item for item in startselected_tasks]
        between_tasks = [item for item in between_tasks]
        dueselected_tasks = [item for item in dueselected_tasks]
        def convert(i):
            return [
                {
                    "id": row[0],
                    "subject": row[1],
                    "project_id": row[2],
                    "project_name": row[3],
                    "start_date": row[4],
                    "due_date": row[5],
                    "author_id" : row[6]
                    
                }
                for row in i
            ]
        startselected_tasks = convert(startselected_tasks)
        between_tasks = convert(between_tasks)
        dueselected_tasks = convert(dueselected_tasks)

        print('start today :', startselected_tasks)
        print('on progress :',between_tasks)
        print('due today :',dueselected_tasks)
        
        # query = "SELECT value FROM custom_values WHERE custom_field_id=4 AND customized_id = idissue"
        # query = "SELECT column_name FROM information_schema.columns WHERE table_schema='bitnami_redmine' AND table_name = 'custom_values'"
        # query = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"

        
    except mysql.connector.Error as e:
        print(f'Error connecting to MySQL database: {e}')

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print('Connection to MySQL database closed')

    def email(list):
        clean = []
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

            for item in list:
                # Create a cursor object
                cursor = connection.cursor()
                responsible_id = []
                query = "SELECT value FROM custom_values WHERE custom_field_id=4 AND customized_id = %s"
                params = (item['id'],)
                cursor.execute(query, params)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        if row == ('',):
                            continue
                        else:
                            print('awal')
                            responsible_id.append(row[0])
                    print(responsible_id)
                
                if responsible_id:
                    for i in responsible_id:
                        query3 = "SELECT a.firstname, a.lastname, b.address FROM users AS a JOIN email_addresses AS b ON a.id = b.user_id WHERE a.id=%s"
                        params3 = (i,)
                        cursor.execute(query3,params3)
                        rows = cursor.fetchall()
                        if rows:
                            for row in rows:
                                responsible = {
                                    'responsible_name' : row[0] + " " + row[1],
                                    'responsible_email' : row[2]
                                }
                            print(responsible)

                        query2 = "SELECT a.firstname, a.lastname, b.address FROM users AS a JOIN email_addresses as b ON a.id = b.user_id WHERE a.id=%s"
                        params2 = (item['author_id'],)
                        cursor.execute(query2, params2)
                        rows = cursor.fetchall()
                        if rows:
                            for row in rows:
                                print(row)
                                author = {
                                    'author_name' : row[0] + " " + row[1],
                                    'author_email' : row[2]
                                }
                        
                            user_info = {
                                'id': item['id'],
                                'subject': item['subject'],
                                'project_id': item['project_id'],
                                'project_name': item['project_name'],
                                'start_date': item['start_date'],
                                'due_date': item['due_date'],
                                'author_email' : author['author_email'],
                                'author_name' : author['author_name'],
                                'name': responsible['responsible_name'],
                                'email': responsible['responsible_email']
                                }
                            clean.append(user_info)
                            
                            
                            if list is startselected_tasks:
                                print("starts")
                                body = f"""
                                Dear {responsible['responsible_name']},

                                You have a task that started today and  will be due on {item['due_date']} from {item['project_name']} Project
                                with task subject : {item['subject']}.

                                View more on : http://redmine.greenfieldsdairy.com/redmine/issues/{item['id']}

                                Regards,
                                {author['author_name']}
                                """
                    
                            elif list is between_tasks:
                                print("between")
                                body = f"""
                                Dear {responsible['responsible_name']},

                                You still have a running task that started from {item['start_date']} and will be due on {item['due_date']}
                                from {item['project_name']} Project with task subject : {item['subject']}.

                                View more on : http://redmine.greenfieldsdairy.com/redmine/issues/{item['id']}

                                Regards,
                                {author['author_name']}
                                """
                            
                            else:
                                print("last")
                                body = f"""
                                
                                Dear {responsible['responsible_name']},

                                You have a task that will be due today on {item['due_date']} from {item['project_name']} Project
                                with task subject : {item['subject']}

                                View more on : http://redmine.greenfieldsdairy.com/redmine/issues/{item['id']}

                                Regards,
                                {author['author_name']}

                                """
                        

                    for i in clean:
                        email_api = "http://10.24.7.70:3333/send-email"
                        payload = {
                            "to": [i['email']],
                            "cc" : [i['author_email']],
                            "subject": f"#{i['id']} [{i['subject']}] Task Reminder",
                            "body": body
                        }

                        print(payload)
                        print('akhir')
                        response = requests.post(email_api, json = payload)

                        if response.status_code == 200:
                            print("Email sent successfully.")
                        else:
                            print(f"Failed to send email. Status code: {response.status_code}")
                            print(response.text)  # Print the response content for debugging
                    
                else:
                    print('gaada')
                    break
                responsible_id.clear()
                author.clear()
                responsible.clear()
        except mysql.connector.Error as e:
            print(f'Error connecting to MySQL database: {e}')

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
                print('Connection to MySQL database closed')

    email(startselected_tasks)
    email(between_tasks)
    email(dueselected_tasks)

    return "Success"
