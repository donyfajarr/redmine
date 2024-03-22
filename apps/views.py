from django.shortcuts import render,redirect
from redminelib import Redmine
import ssl
from openpyxl import load_workbook
from datetime import datetime, timedelta,date
from . import models
import mysql.connector
from django.http import JsonResponse
import requests


ssl._create_default_https_context = ssl._create_unverified_context
key = "a435e1173a8238a1fb5fd6d07bc8042c901abbfd"
redmine = Redmine('https://redmine.greenfieldsdairy.com/redmine', key=key, requests={'verify': False,})
users = []
# Create your views here.


# DASHBOARD
def index(request):
    users = redmine.user.get('current')
    user = users.id
    listproject = []
    selected_tasks = []
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
        query1 = "SELECT projects.id, projects.name FROM projects JOIN members ON projects.id = members.project_id WHERE members.user_id = %s ORDER BY projects.name ASC "
        today_date = date.today() + timedelta(days=3)
        start_date = date(today_date.year, today_date.month, today_date.day)
        author_id = user
        cursor.execute(query1, (author_id,))
        rows1 = cursor.fetchall()
        if rows1:
            for row in rows1:
                list = {}
                list['id'] = row[0]
                list['name'] = row[1]
                listproject.append(list)
        
        query2 = "SELECT issues.id, issues.subject, issues.due_date, issues.project_id, projects.name FROM issues JOIN projects ON issues.project_id = projects.id WHERE author_id = %s AND due_date <= %s"

        cursor.execute(query2, (author_id, start_date))
        rows2 = cursor.fetchall()
        p = len(rows2)
        print(p)
        if rows2:
            for row in rows2:
                task_info = {
                'id' : row[0],
                'name' : row[1],
                'project' : row[4],
                'due_date' : row[2]
                }
                selected_tasks.append(task_info)
                if len(selected_tasks) == 3:
                    break
        else:
            print("No rows found matching the criteria.")

    except mysql.connector.Error as e:
        print(f'Error connecting to MySQL database: {e}')

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print('Connection to MySQL database closed')

    sum = len(listproject)
    if request.method == "POST":
        go = request.POST['go']
        return redirect ('listissue', id=str(go))

    return render(request,'index.html',{
        'selected_tasks' : selected_tasks,
        'p' : p,
        'name' : users['firstname'] +' ' + users['lastname'],
        'listproject' : listproject,
        'sum' : sum
    }) 

# PROJECT
def listproject(request):
    listproject = []
    for i in redmine.project.all():
        list = []
        list.append(i.name)
        list.append(i.identifier)
        listproject.append(list)
    return render(request, 'listproject.html',{
        'listproject' : listproject
    })
def updateproject(request,id):
    update = redmine.project.get(id)
    if request.method == "GET":
        return render(request, 'updateproject.html',{
            'update' : update,
            'listproject' : listproject
        })
    else:
        update.description = request.POST['description']
        update.is_public = eval(request.POST['is_public'])
        update.save()
        return redirect('listproject')
def newproject(request):
    listproject = []
    new = redmine.project.new()
    getparent = redmine.project.all()
    for i in getparent:
        listproject.append(i)
    if request.method == "GET":
        return render (request, 'newproject.html',{
            'listproject' : listproject
        })
    elif request.method == "POST":
        new.name = request.POST['name']
        if " " in request.POST['name']:
            name = request.POST['name'].replace(" ", "")
            new.identifier = name
        else:
            new.identifier = request.POST['name']
        new.description = request.POST['description']
        new.is_public = eval(request.POST['is_public'])
        if request.POST['parent'] == "kosong":
            pass
        else:
            new.parent_id = request.POST['parent']
        new.save()
        return redirect ('confirmation', name=request.POST['name'])
def confirmation (request, name):
    
    if request.method == 'POST':
        allstatus = models.status.objects.all()
        alldept = models.dept.objects.all()
        alluser = models.user.objects.all()
        allpriority = models.priority.objects.all()
        forprint = list()
        if 'upload' in request.POST:
            files = request.FILES['filea']
            wb = load_workbook(files)
            ws = wb.active
            start_row = 5
            # jadi input di htmlnya
            # col3_idx = {}
            col3_values = []
            col4_values = []
            col2_values = []
            col2_idx  = {}
            col5_values = []
            col6_values = []
            taskx = []

            def get_date_range_for_week(year, week_start, week_end):
                if week_start is None or week_start < 1:
                    return []
                first_day = datetime(year, 1, 1)
                def calculate_week_dates(week_number):
                    offset = (week_number - 1) * 7
                    start_date = first_day + timedelta(days=offset)
                    end_date = start_date + timedelta(days=4)
                    return start_date, end_date
                if week_end is None:
                    start_date, end_date = calculate_week_dates(week_start)
                    return [(start_date, end_date)]  # Return a list containing a single tuple
                elif week_start is not None and week_end is not None and week_end >= week_start:
                    start_date = calculate_week_dates(week_start)[0]
                    end_date = calculate_week_dates(week_end)[1]
                    return [(start_date, end_date)]
                else:
                    return []
            def find_col_with_filled_color(ws, row_index):
                filled_cells = []
                for col_index in range(9, ws.max_column + 1):
                    cell = ws.cell(row=row_index, column=col_index)
                    
                    if isinstance(cell.fill.fgColor.theme, int) or (cell.fill.fgColor.rgb != 'FFFF0000' and  cell.fill.fgColor.rgb !='00000000'):
                        findweek = ws.cell(4, col_index).value
                        filled_cells.append(findweek)

                return filled_cells if filled_cells else None
            
            for row_idx, (cell_value) in enumerate(ws.iter_rows(min_row=start_row,min_col=2,max_col=2, values_only=True), start=start_row):
                col2_values.append(cell_value)
                col2_idx[cell_value] = row_idx
            for row in ws.iter_rows(min_row=start_row, min_col=3, max_col=3, values_only=True):
                cell_value = row[0] if row and row[0] is not None else None
                col3_values.append(cell_value)
            for row in ws.iter_rows(min_row=start_row, min_col=4, max_col=4, values_only=True):
                cell_value = row[0] if row and row[0] is not None else None
                col4_values.append(cell_value)
            for row in ws.iter_rows(min_row=start_row, min_col=5, max_col=5, values_only=True):
                cell_value = row[0] if row and row[0] is not None else None
                col5_values.append(cell_value)
            for row in ws.iter_rows(min_row=start_row, min_col=6, max_col=6, values_only=True):
                cell_value = row[0] if row and row[0] is not None else None
                col6_values.append(cell_value)
            
            
            tasks_data = []
            current_task = None
            temp = []
            temp2 = []
            temp3 = []
            temp4 = []
            for idx, value in enumerate(col2_values):
                if value[0] is not None:
    
                    taskx.append(col2_idx[value])
                    p = find_col_with_filled_color(ws,col2_idx[value])
                    if p is not None:
                        if len(p)>1:
                            week_start = min(p)
                            week_end = max(p)
                        else:
                            week_start = min(p)
                            week_end = None
                        
                        get_ranges = get_date_range_for_week(2024, week_start, week_end)
                        for start_date, end_date in get_ranges:
                            start_date = start_date.strftime('%Y-%m-%d')
                            end_date = end_date.strftime('%Y-%m-%d')
                    else:
                        week_start = None
                        week_end = None
                        start_date = week_start
                        end_date = week_end

                    findpic = ws.cell(col2_idx[value], 8).value
                    if findpic is not None:
                        findpic = findpic.upper()
                    findperson = ws.cell(col2_idx[value], 61).value
                    if findperson is not None:
                        if ',' in findperson:
                            findperson.split('')
                        findperson = findperson
                    current_task = {'name': value[0], 'start_date':start_date, 'due_date':end_date, 'pic' : findpic, 'person': findperson, 'subtasks': {}, }
                    tasks_data.append(current_task)
                    temp = []
                elif current_task is not None:
                    subtask_value = col3_values[idx] if idx < len(col3_values) else None
                    
                    if subtask_value is not None:
                        
                        p = find_col_with_filled_color(ws,idx+start_row)
                    
                        if p is not None:
                            if len(p)>1:
                                week_start = min(p)
                                week_end = max(p)
                            else:
                                week_start = min(p)
                                week_end = None
                        else:
                            week_start = None
                            week_end = None
                        get_ranges =  get_date_range_for_week(2024, week_start, week_end)

                        for start_date, end_date in get_ranges:
                            start_date = start_date.strftime('%Y-%m-%d')
                            end_date = end_date.strftime('%Y-%m-%d')
                     
                        findpic = ws.cell(idx+start_row, 8).value
                        if findpic is not None:
                            findpic = findpic.upper()
                        findperson = ws.cell(idx+start_row, 61).value
                        if findperson is not None:
                            findperson = findperson
                        add = {'name' : subtask_value, 'pic': findpic, 'start_date' : start_date, 'due_date' : end_date, 'person':findperson, 'subtasks' : {} }
                        temp.append(add)
                        current_task['subtasks'] = temp

                    else:
                        subtask_value = col4_values[idx] if idx < len(col4_values) else None
                        if subtask_value is not None:
                            p = find_col_with_filled_color(ws,idx+start_row)
                        
                            if p is not None:
                                if len(p)>1:
                                    week_start = min(p)
                                    week_end = max(p)
                                else:
                                    week_start = min(p)
                                    week_end = None
                            else:
                                week_start = None
                                week_end = None
                            get_ranges =  get_date_range_for_week(2024, week_start, week_end)

                            for start_date, end_date in get_ranges:
                                start_date = start_date.strftime('%Y-%m-%d')
                                end_date = end_date.strftime('%Y-%m-%d')
                        
                            findpic = ws.cell(idx+start_row, 8).value
                            if findpic is not None:
                                findpic = findpic.upper()
                            findperson = ws.cell(idx+start_row, 61).value
                            if findperson is not None:
                                if ',' in findperson:
                                    findperson.split('')
                                findperson = findperson
                            add2 = {'name' : subtask_value, 'pic': findpic, 'start_date' : start_date, 'due_date' : end_date, 'person':findperson, 'subtasks' : {}}
                            temp2.append(add2)
                            add['subtasks'] = temp2
                            # print(add2)
                        else:
                            temp2 = []  
                            subtask_value = col5_values[idx] if idx < len(col5_values) else None
                            if subtask_value is not None:
                                p = find_col_with_filled_color(ws,idx+start_row)
                                if p is not None:
                                    if len(p)>1:
                                        week_start = min(p)
                                        week_end = max(p)
                                    else:
                                        week_start = min(p)
                                        week_end = None
                                else:
                                    week_start = None
                                    week_end = None
                                get_ranges =  get_date_range_for_week(2024, week_start, week_end)

                                for start_date, end_date in get_ranges:
                                    start_date = start_date.strftime('%Y-%m-%d')
                                    end_date = end_date.strftime('%Y-%m-%d')
                            
                                findpic = ws.cell(idx+start_row, 8).value
                                if findpic is not None:
                                    findpic = findpic.upper()
                                findperson = ws.cell(idx+start_row, 61).value
                                if findperson is not None:
                                    if ',' in findperson:
                                        findperson.split('')
                                findperson = findperson
                                add3 = {'name' : subtask_value, 'pic': findpic, 'start_date' : start_date, 'due_date' : end_date, 'person':findperson,'subtasks' : {} }
                                temp3.append(add3)
                                add2['subtasks'] = temp3
                                
                            else:
                                
                                temp3 = []
                                subtask_value = col6_values[idx] if idx < len(col6_values) else None
                          
                                if subtask_value is not None:
                                    p = find_col_with_filled_color(ws,idx+start_row)
                                  
                                    if p is not None:
                                        if len(p)>1:
                                            week_start = min(p)
                                            week_end = max(p)
                                        else:
                                            week_start = min(p)
                                            week_end = None
                                    else:
                                        week_start = None
                                        week_end = None
                                    get_ranges =  get_date_range_for_week(2024, week_start, week_end)

                                    for start_date, end_date in get_ranges:
                                        start_date = start_date.strftime('%Y-%m-%d')
                                        end_date = end_date.strftime('%Y-%m-%d')
                                
                                    findpic = ws.cell(idx+start_row, 8).value
                                    if findpic is not None:
                                        findpic = findpic.upper()
                                    findperson = ws.cell(idx+start_row, 61).value
                                    if findperson is not None:
                                        if ',' in findperson:
                                            findperson.split('')   
                                    add4 = {'name' : subtask_value, 'pic': findpic, 'start_date' : start_date,'person':findperson, 'due_date' : end_date }
                                    temp4.append(add4)
                                    add3['subtasks'] = temp4
                                else:
                                    temp4 = []
                else:
                    pass
            
          
            def process_tasks(tasks, parent_name=None):
                for task in tasks:
                    task['Parent'] = parent_name
                    forprint.append(task)
                    if 'subtasks' in task and task['subtasks']:
                        process_tasks(task['subtasks'], parent_name=task['name'])

            process_tasks(tasks_data)
            user = redmine.user.get('current')
            request.session['forprint'] = forprint
            for item in forprint:
                print(item)
            request.session['name'] = name

            return render (request, 'confirmation.html', {
                'name' : name,
                'tasks_data' : forprint,
                'alluser' : alluser,
                'user' : user,
                'allstatus' : allstatus,
                'alldept' : alldept,
                'allpriority' : allpriority
            })
        else:
            forprint = request.session.get('forprint',[])
            name = request.session.get('name',[])
            def create_issue(item):
                id = name
                form_name = f'name_{item['name']}'
               
                form_description = f'description_{item['name']}'
                form_start_date = f'start_date_{item['name']}'
                form_due_date = f'due_date_{item['name']}'
                form_assigned_to = f'assigned_to_{item['name']}'
                form_department = f'department_{item['name']}[]'
                form_responsible = f'responsible_{item['name']}[]'
                form_status= f'status_{item['name']}'
                form_priority = f'priority_{item['name']}'
                form_estimated_hours = f'estimated_hours_{item['name']}'
                form_done_ratio = f'done_ratio_{item['name']}'
                form_parent = f'parenttask_{item['name']}'
                parent = request.POST.get(form_parent)
                subject = request.POST.get(form_name)
                start_date = request.POST.get(form_start_date)
                due_date = request.POST.get(form_due_date)
                assigned_to = request.POST.get(form_assigned_to)
                description = request.POST.get(form_description)
                status = request.POST.get(form_status)
                priority = request.POST.get(form_priority)
                estimated_hours = request.POST.get(form_estimated_hours)
                done_ratio = request.POST.get(form_done_ratio)
                department = request.POST.getlist(form_department)
                responsible = request.POST.getlist(form_responsible)
                nama_parent = form_parent.split("_")
                nama_parent = nama_parent[1]
                create = redmine.issue.new()
                if parent is not None:
                    parent_issue_id = redmine.issue.filter(project_id = id, subject=parent)
                    for i in parent_issue_id:
                        # print(i.id)
                        create.parent_issue_id = i.id
                else:
                    print('gamasuk')
                create.project_id = id
                create.subject=subject
                create.description = description
                create.assigned_to_id = assigned_to
                create.start_date=start_date
                create.due_date=due_date
                create.status=status
                create.priority=priority
                create.estimated_hours=estimated_hours
                create.done_ratio=done_ratio
                create.custom_fields=[{'id':11, 'value':department}]
                create.custom_fields=[{'id':4, 'value':responsible}]
                create.save()

            first_condition_items = []
            second_condition_items = []
            last_condition_items = []
        
            for item in forprint:
                if item.get('Parent') is None:
                    first_condition_items.append(item)
                elif item.get('subtasks') is not None and item.get('Parent') is not None:
                    second_condition_items.append(item)
                elif item.get('subtasks') is None and item.get('Parent') is not None:
                    last_condition_items.append(item)
                else:
                    print('stillexists')
           
            for item in first_condition_items:
                print('first')
                create_issue(item)
            for item in second_condition_items:
                print('second')
                create_issue(item)
            for item in last_condition_items:
                print('last')
                create_issue(item)
              

            return redirect('listproject')
        
    return render(request, 'confirmation.html', {\
        })

# ISSUE
def listissue(request,id):
    global users
    listissue = []
    find = redmine.issue.filter(project_id=id,sort='start_date:asc')
    if request.method == "GET":
        for item in find:
            tes = []
            tes.append(item.id)
            tes.append(item.subject)
            tes.append(str(item.status))
            try:
                tes.append(item.assigned_to)
            except:
                tes.append('-')
            tes.append(item.start_date)
            tes.append(item.due_date)
            listissue.append(tes)
        
        # if models.user.objects.exists():
        #     pass
        # else:
            for i in range(1,77):
                try:
                    user = redmine.user.get(i)
                    for item in user:
                        print(item)
                        # models.user.objects.create(id=i, name = user.firstname +' '+user.lastname)
                        
                except:
                    continue
        
        return render(request, 'listissue.html',{
        'listissue' : listissue,
        'id' : id
    })

    elif request.method == "POST":
        tes = redmine.issue.filter(project_id='master-project')
        tes.export('csv', savepath='../redmine/', columns='all')    
        return redirect('listissue')
    
def listdetails(request,id):
    get = redmine.issue.get(id)
    
    dict = {}
    listresponsible = []
    listdepartment = []
    dict['subject'] = get.subject
    dict['id'] = get.id
    dict['description'] = get.description
    dict['status'] = get.status
    dict['priority'] = get.priority
    dict['assigned_to'] = '-'
    
    try:
        if get.custom_fields[0]['value']:
            for i in get.custom_fields[0]['value']:
                user = models.user.objects.get(id=int(i))
                listresponsible.append(user.name)
            listresponsible = ', '.join(listresponsible)
            dict['responsible'] = listresponsible
        else:
            dict['responsible'] = '-'
    except:
        pass
    try:
        if dict['assigned_to']:
            
            dict['assigned_to'] = get.assigned_to
    except:
        pass
    try:
        if get.custom_fields[7]['value']:
            for i in get.custom_fields[7]['value']:
                    listdepartment.append(i)
            listdepartment = ', '.join(listdepartment)
            dict['department'] = listdepartment
        else:
            dict['department'] = '-'
    except:
        pass
    


    relation  = redmine.issue_relation.filter(issue_id = id)
    if relation:
        list = {}
        issue_id = []
        relation_type = []
        issue_to_id = []
        for i in relation:
            issue_id.append(i['issue_id'])
            issue_to_id.append(i['issue_to_id'])
            relation_type.append(i['relation_type'].capitalize())
        list['issue_id'] = issue_id
        list['relation_type'] = relation_type
        list['issue_to_id'] = issue_to_id
        dict['relation'] = list
        relation_str = ""
        for issue_id, issue_to_id, relation_type in zip(issue_id, issue_to_id, relation_type):
            relation_str += f"<a href='/listdetails/{issue_id}'>#{issue_id}</a> {relation_type} to <a href='/listdetails/{issue_to_id}'>#{issue_to_id}</a>, "
        relation_str = relation_str[:-2]
        dict['relation'] = relation_str

    else:
        dict['relation'] = '-'

    
    dict['start_date'] = get.start_date
    dict['due_date'] = get.due_date
    dict['estimated_hours'] = get.estimated_hours
    dict['done_ratio'] = get.done_ratio


    if models.user.objects.exists():
        pass
    else:
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

            # Define the SQL query
            query = "SELECT users.id, users.firstname, users.lastname, email_addresses.user_id, address FROM users JOIN email_addresses ON users.id = email_addresses.user_id"
            # query = "SELECT user_id, address FROM email_addresses"
            # query = "SELECT column_name FROM information_schema.columns WHERE table_schema='bitnami_redmine' AND table_name = 'users'"
            # query = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE';"

            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                # print(row)
                id, firstname, lastname, users_id, email = row
                # print(id)
                # try:
                # models.user.objects.all().delete()
                models.user.objects.create(id=id,name=firstname+ ' ' +lastname, email=email)
                    # getmodel.email = email
                    # getmodel.save()
                # except:
                #     print('not exists')


        except mysql.connector.Error as e:
            print(f'Error connecting to MySQL database: {e}')

        finally:
            # Close cursor and connection
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
                print('Connection to MySQL database closed')

   
    return render(request, 'listdetails.html',{
        'dict' : dict
    })
def newissue(request):
    user = redmine.user.get('current')
    alldept = models.dept.objects.all()
    allstatus = models.status.objects.all()
    allpriority = models.priority.objects.all()
    alluser = models.user.objects.all()
    listproject = []
    for i in redmine.project.all():
        list = {}
        list['name'] = i.name
        list['id'] = i.identifier
        listproject.append(list)
    if request.method == "GET":
        return render(request, 'newissue.html',{
            'all' : all,
            'user' : user,
            'listproject' : listproject,
            'allstatus' : allstatus,
            'alldept' : alldept,
            'allpriority' : allpriority,
            'alluser' : alluser
        })
    else:
        new = redmine.issue.new()
        
        new.project_id = request.POST['id']
        new.subject = request.POST['subject']
        new.description = request.POST['description']

        p = request.POST['status']
        getstatus = models.status.objects.get(id=p)
        new.status_id = getstatus.id
        pri = request.POST['priority']
        getpriority = models.priority.objects.get(id=pri)
        new.priority_id = getpriority.id
        new.assigned_to_id = request.POST['assigned_to']
        responsible = request.POST.getlist('responsible[]')
        department = request.POST.getlist('department[]')
        new.custom_fields=[{'id':4, 'value':responsible}]
        new.custom_fields=[{'id':11, 'value':department}]
        new.estimated_hours = request.POST['estimated_hours']
        new.start_date = request.POST['start_date']
        new.due_date = request.POST['due_date']
        # new.parent_issue_id = request.POST['parent']
        new.done_ratio = request.POST['done_ratio']
        print('jalan')
        new.save()
        return redirect('listproject')
def updateissue(request,id):
    listdept = []
    listresponsible = []
    update = redmine.issue.get(id)
    start_date = datetime.strftime(update.start_date, '%Y-%m-%d')
    due_date = datetime.strftime(update.due_date, '%Y-%m-%d')
    alluser = models.user.objects.all()
    allstatus = models.status.objects.all()
    allpriority = models.priority.objects.all()
    alldept = models.dept.objects.all()
    dept = update.custom_fields
    for i in update.custom_fields[0]['value']:
        listresponsible.append(int(i))
    for i in dept[7]['value']:
        listdept.append(i)
    if request.method == "GET":
        
        return render(request, 'updateissue.html',{
            'id' : id,
            'update' : update,
            'alluser' : alluser,
            'listdept' : listdept,
            'allstatus' : allstatus,
            'allpriority' : allpriority,
            'alldept' : alldept,
            'start_date' : start_date,
            'due_date' : due_date,
            'listresponsible' : listresponsible
        })
    else:
        update.subject = request.POST['subject']
        p = request.POST['status']
        getstatus = models.status.objects.get(id=p)
        update.status_id = getstatus.id
        update.description = request.POST['description']
        department = request.POST.getlist('department[]')
        update.custom_fields=[{'id':11,'value':department}]
        update.start_date = request.POST['start_date']
        update.due_date = request.POST['due_date']
        pri = request.POST['priority']
        getpriority = models.priority.objects.get(id=pri)
        update.priority_id = getpriority.id
        
        update.assigned_to_id = request.POST['assigned_to']
        responsible = request.POST.getlist('responsible[]')
        
        update.custom_fields=[{'id':4, 'value':responsible}]
    
        update.estimated_hours = request.POST['estimated_hours']
        update.done_ratio = request.POST['done_ratio']

        update.save()
        return redirect('listdetails',id=id)
    
def deleteissue(request,id):
    delete = redmine.issue.get(id)
    p = delete['project']
    delete.delete()
    return redirect('listissue', id=p)

# NOTES TO IMPROVE
#  - Subissue dan related issue (waktu create issue ataupun import) *blum solved algonya
#  - Update interface untuk yang diassign only/menerima task (multi user authentication)
#  - Gantt chart (berat dan ribet dependencies)
#  - Import excel tapi di existing project




def addrelations(request,id):
    if request.method == "GET":
        get = redmine.issue.filter(project_id = id)
        return render(request, 'addrelation.html',{
            'get':get
        })
    else:

        target = redmine.issue_relation.new()
        target.issue_id = request.POST['issue_id']
        target.issue_to_id = request.POST['issue_to_id']
        target.relation_type = request.POST['relation_type']
        target.save()
        return redirect ('listissue', id=id)

    # SET REMINDER EMAIL
def testing(request):
    if request.method == "GET":
        user = redmine.user.get('current')
        user = user.id
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
                "SELECT issues.id, issues.subject, issues.project_id, projects.name, issues.start_date, issues.due_date FROM issues JOIN projects ON issues.project_id = projects.id WHERE assigned_to_id = %s AND start_date = %s",
                "SELECT issues.id, issues.subject, issues.project_id, projects.name, issues.start_date, issues.due_date FROM issues JOIN projects ON issues.project_id = projects.id WHERE assigned_to_id = %s AND start_date <= %s AND %s <= due_date",
                "SELECT issues.id, issues.subject, issues.project_id, projects.name, issues.start_date, issues.due_date FROM issues JOIN projects ON issues.project_id = projects.id WHERE assigned_to_id = %s AND due_date = %s",

            ]
            today_date = date.today()
            start_date = date(today_date.year, today_date.month, today_date.day)
            params_list = [
                (user, start_date),
                (user, start_date, start_date),
                (user, start_date)
            ]
            results = []
            for queries, params in zip(query, params_list):
                cursor.execute(queries,params)
                rows=cursor.fetchall()
                results.append(rows)
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
                        "due_date": row[5]
                    }
                    for row in i
                ]
            startselected_tasks = convert(startselected_tasks)
            between_tasks = convert(between_tasks)
            dueselected_tasks = convert(dueselected_tasks)

            print(startselected_tasks)
            print(between_tasks)
            print(dueselected_tasks)
            # query = "SELECT * FRO"
            # query = "SELECT table_name FROM information_schema.tables WHERE table_schema='bitnami_redmine'"
            # query = "SELECT user_id, address FROM email_addresses"
            # query = "SELECT column_name FROM information_schema.columns WHERE table_schema='bitnami_redmine' AND table_name = 'projects'"
            # query = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
            # cursor.execute(query)
            # Execute the query

            # Fetch all the rows
            # rows = cursor.fetchall()
            # if rows:
                # Process the rows
                # for row in rows:
                #     print(row)
            # else:
                # print("No rows found matching the criteria.")

         
        except mysql.connector.Error as e:
            print(f'Error connecting to MySQL database: {e}')

        finally:

            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
                print('Connection to MySQL database closed')

        def email(list):
            for item in list:
                get_issue = redmine.issue.get(item['id'])
                if get_issue.custom_fields[0]['value']:
                    for i in get_issue.custom_fields[0]['value']:
                        user = models.user.objects.get(id=int(i))
                        item['name'] = user.name
                        item['email'] = user.email
                    if list is startselected_tasks:
                        print("starts")
                        body = f"""
                        Dear {item['name']},

                        You have a task that started today and  will be due on {item['due_date']} from {item['project_name']}
                        with task subject : {item['subject']}
                        """
                    elif list is between_tasks:
                        print("between")
                        body = f"""
                        Dear {item['name']},

                        You still have a running task that started from {item['start_date']} and will be due on {item['due_date']}
                        from {item['project_name']} with task subject : {item['subject']}
                        """
                    else:
                        print("last")
                        body = f"""
                        
                        Dear {item['name']},

                        You have a task that will be due today on {item['due_date']} from {item['project_name']}
                        with task subject : {item['subject']}


                        """
                    email_api = "http://10.24.7.70:3333/send-email"
                    payload = {
                        "to": [item['email']],
                        "subject": f"#{item['id']} [{item['subject']}] Task Reminder",
                        "body": body
                    }

                    # print(payload)
                    # response = requests.post(email_api, json = payload)

                    # if response.status_code == 200:
                    #     print("Email sent successfully.")
                    # else:
                    #     print(f"Failed to send email. Status code: {response.status_code}")
                    #     print(response.text)  # Print the response content for debugging
                else:
                    print('gaada')
                    break

        email(startselected_tasks)
        email(between_tasks)
        email(dueselected_tasks)
        
        return render(request, "testing.html",{

    })