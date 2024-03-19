from django.shortcuts import render,redirect
from redminelib import Redmine
import ssl
from openpyxl import load_workbook
from datetime import datetime, timedelta
from . import models


ssl._create_default_https_context = ssl._create_unverified_context
key = "a435e1173a8238a1fb5fd6d07bc8042c901abbfd"
redmine = Redmine('https://redmine.greenfieldsdairy.com/redmine', key=key, requests={'verify': False,})
users = []
# Create your views here.

# DASHBOARD
def index(request):
    listproject = []
    for i in redmine.project.all():
        list = {}
        list['name'] = i.name
        list['id'] = i.identifier
        listproject.append(list)
    sum = len(listproject)
    user = redmine.user.get('current')
    users = user.issues
    selected_tasks = []
    p = len(users)
    due_date_threshold = datetime.now().date() + timedelta(days=3)
    for i in reversed(users):
        if i['due_date'] and i['due_date'] <= due_date_threshold:
            task_info = {
                'id' : i['id'],
                'name': i['subject'],
                'project': i['project']['name'],
                'due_date': i['due_date']
            }
            selected_tasks.append(task_info)
            if len(selected_tasks) == 3:
                break
    if request.method == "POST":
        go = request.POST['go']
        return redirect ('listissue', id=str(go))

    return render(request,'index.html',{
        'selected_tasks' : selected_tasks,
        'p' : p,
        'name' : user['firstname'] +' ' + user['lastname'],
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
            col3_idx = {}
            col3_values = []
            col4_values = []
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
            
            for row_idx, (cell_value,) in enumerate(ws.iter_rows(min_row=start_row, min_col=3, max_col=3, values_only=True), start=start_row):
                col3_values.append(cell_value)
                col3_idx[cell_value] = row_idx
            for row in ws.iter_rows(min_row=start_row, min_col=4, max_col=4, values_only=True):
                cell_value = row[0] if row and row[0] is not None else None
                col4_values.append(cell_value)
            
            
            tasks_data = []
            current_task = None
            temp = []
            for idx, value in enumerate(col3_values):
                if value is not None:
                    taskx.append(col3_idx[value])
                    p = find_col_with_filled_color(ws,col3_idx[value])
       
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
                    get_ranges = get_date_range_for_week(2024, week_start, week_end)
         
                    for start_date, end_date in get_ranges:
                        start_date = start_date.strftime('%Y-%m-%d')
                        end_date = end_date.strftime('%Y-%m-%d')
              
                    findpic = ws.cell(col3_idx[value], 8).value
                    if findpic is not None:
                        findpic = findpic.upper()
                    current_task = {'name': value, 'start_date':start_date, 'due_date':end_date, 'pic' : findpic, 'subtasks': {}, }
                    tasks_data.append(current_task)
                    temp = []
                elif current_task is not None:
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
                        add = {'name' : subtask_value, 'pic': findpic, 'start_date' : start_date, 'due_date' : end_date }
                        temp.append(add)
                        current_task['subtasks'] = temp
            
            for item in tasks_data:
                if item['subtasks']:
                    forprint.append(item)
                    for i in item['subtasks']:
                        i['Parent'] = item['name']
                        forprint.append(i)
    
                else:
        
                    forprint.append(item)
            user = redmine.user.get('current')
            request.session['forprint'] = forprint
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

            for item in forprint:
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
                responsible=request.POST.getlist(form_responsible)
                create = redmine.issue.new()
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
        
        if models.user.objects.exists():
            pass
        else:
            for i in range(1,77):
                try:
                    user = redmine.user.get(i)
                    models.user.objects.create(id=i, name = user.firstname +' '+user.lastname)
                except:
                    continue
        
        return render(request, 'listissue.html',{
        'listissue' : listissue
    })

    elif request.method == "POST":
        tes = redmine.issue.filter(project_id='master-project')
        tes.export('csv', savepath='../redmine/', columns='all')    
        return redirect('listissue')
    
def listdetails(request,id):
    get = redmine.issue.get(id)
    
    # INI NAMBAH RELATED ISSUE

    # target = redmine.issue_relation.new()
    # target.issue_id = id
    # target.issue_to_id = 11122
    # target.relation_type = 'precedes'
    # target.save()

    dict = {}
    listresponsible = []
    listdepartment = []
    dict['subject'] = get.subject
    dict['id'] = get.id
    dict['description'] = get.description
    dict['status'] = get.status
    dict['priority'] = get.priority
    dict['assigned_to'] = '-'
    # dict['responsible'] = get.custom_fields(['id']==11)
    
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
    


    dict['start_date'] = get.start_date
    dict['due_date'] = get.due_date
    dict['estimated_hours'] = get.estimated_hours
    dict['done_ratio'] = get.done_ratio
    
   
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