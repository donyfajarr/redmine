from functools import wraps
from django.shortcuts import redirect
from redminelib import Redmine

def check_login_session(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('username') and request.session.get('password'):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper

def initialize_redmine(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        global redmine
        
        username = request.session.get('username')
        password = request.session.get('password')
        print('naah')
        if username and password:
            print('asup')
            redmine = Redmine('https://redmine.greenfieldsdairy.com/redmine', 
                                username=username, 
                                password=password, 
                                requests={'verify': False})
        print(redmine)
        kwargs['redmine'] = redmine
        return view_func(request, *args, **kwargs)
    return wrapper