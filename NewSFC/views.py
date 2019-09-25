from django.shortcuts import render
from django.shortcuts import redirect
import requests
import json

from board.views import natip

def sfcaddpage(request):
    return render(request, 'sfcaddpage.html', {})

def sfclist(request):
    rulelist_result = {"rulelist":"test"}
#    if request.method == 'POST': 
    rulelist_command = "ip r|grep static"
    rulelist_command_post_data = {"command":rulelist_command}
    rulelist_result = {"rulelist":"unknow"}
    try:
        print("------")
        rulelist_result = json.loads(requests.post("http://"+natip+"/nat/rulelist", rulelist_command_post_data, timeout=30).content.decode('utf-8'))
    except Exception as e:
        rulelist_result = {"rulelist":"false"}
    return render(request, "sfclist.html", {"rulelist":rulelist_result["rulelist"]})

def sfcaction(request):
    if request.method == 'POST':
        if request.POST.get('Delete'):
            pass
        elif request.POST.get('AddPage'):
            return render(request, 'sfcaddpage.html', {})
        elif request.POST.get('Return'):
            return redirect('/sfcaddpage/')
        elif request.POST.get('Apply'):
            pass
    else:
        return render(request, 'sfclist.html', {})
