from datetime import datetime
from django.shortcuts import render
import requests
import json
from board.views import fwip
from board.views import idsip
from board.views import dpiip
from board.views import wafip

from board.views import natip
from board.views import gwip


service1_domain = "172.17.1.0/24"
service2_domain = "172.17.2.0/24"
nat_address = "172.17.0.253"
gw_address = "172.17.0.3"
gw_address2 = "172.17.1.254"
fw_address = "172.17.0.201"
ids_address = "172.17.0.202"
dpi_address = "172.17.0.203"
waf_address = "172.17.0.204"

fw_interface = "ens33"
ids_interface = "ens33"
dpi_interface = "ens33"
waf_interface = "ens33"
nat_interface = "ens33"
gw_interface = "ens33"

class service_order:
    def __init__(self):
        self.fw_order = -1
        self.ids_order = -1
        self.dpi_order = -1
        self.waf_order = -1

def get_order(request, j, service_order, orderlist, myOrderlist):
    myOrderlist.append(nat_address)
    for i in range(len(orderlist)):
        service = request.POST['sel' + str(j) + str(i)] 

        if service == "不執行":
            pass
        else:
            if i == 0:
                service = int(service) - 1
                orderlist[service] = []
                orderlist[service].append("FW")
                orderlist[service].append(fw_address)
            elif i == 1:
                service = int(service) - 1
                orderlist[service] = []
                orderlist[service].append("IDS")
                orderlist[service].append(ids_address)
            elif i == 2:
                service = int(service) - 1
                orderlist[service] = []
                orderlist[service].append("DPI")
                orderlist[service].append(dpi_address)
            elif i == 3:
                service = int(service) - 1
                orderlist[service] = []
                orderlist[service].append("WAF")
                orderlist[service].append(waf_address)
    
    # 刪除多餘list
    while None in orderlist:
        orderlist.remove(None)
    for i in range(len(orderlist)):
        myOrderlist.append(orderlist[i][1])
        if(orderlist[i][1]==fw_address):
            service_order.fw_order = i+1
        elif(orderlist[i][1]==ids_address):
            service_order.ids_order = i+1
        elif(orderlist[i][1]==dpi_address):
            service_order.dpi_order = i+1
        elif(orderlist[i][1]==waf_address):
            service_order.waf_order = i+1
    myOrderlist.append(gw_address)
    return service_order, orderlist, myOrderlist

def check_route():
    nat_check_command = "traceroute "+gw_address2
    nat_check_post_data = {"command":nat_check_command}
    nat_check_r = {"order":"unknow"}
    try :
        nat_check_r = json.loads(requests.post("http://"+natip+"/nat/traceroute", nat_check_post_data, timeout=30).content.decode('utf-8'))
        nat_check_r['order'] = nat_check_r['order'].replace(fw_address,"FW").replace(ids_address,"IDS").replace(dpi_address,"DPI").replace(waf_address,"WAF").replace(gw_address2+">","").replace(">"+gw_address+">"+gw_address+">","")
    except Exception as e:
        nat_check_r = {"order":"false"}
    return nat_check_r

def chain(request):
    orderlist1 = [None]*4
    orderlist2 = [None]*4

    myOrderlist1 = []
    myOrderlist2 = []

    flow1_order = service_order()
    flow2_order = service_order()
    
    nat_command = ""
    fw_command = ""
    ids_command = ""
    dpi_command = ""
    waf_command = ""
    gw_command = ""

    nat_check_r = ""

    nat_check_command = "traceroute "+gw_address2
    nat_check_post_data = {"command":nat_check_command}
    nat_check_r = {"order":"unknow"}
    try :
        nat_check_r = json.loads(requests.post("http://"+natip+"/nat/traceroute", nat_check_post_data,timeout=30).content.decode('utf-8'))
        nat_check_r['order'] = nat_check_r['order'].replace(fw_address,"FW").replace(ids_address,"IDS").replace(dpi_address,"DPI").replace(waf_address,"WAF").replace(gw_address2+">","").replace(">"+gw_address+">"+gw_address+">","")

    except Exception as e:
        nat_check_r = {"order":"false"}

    # 獲得網路服務排序 
    if request.method == "POST":
       
        flow1_order, orderlist1, myOrderlist1 = get_order(request, 1, flow1_order, orderlist1, myOrderlist1)
        flow2_order, orderlist2, myOrderlist2 = get_order(request, 2, flow2_order, orderlist2, myOrderlist2)
       

        if len(orderlist1) == 0 and len(orderlist2) == 0:
            nat_command = "sudo nmcli con modify " + nat_interface + " ipv4.routes \"" + service1_domain + " " + gw_address + "\" +ipv4.routes \"" + service2_domain + " " + gw_address + "\" ; sudo systemctl restart network;"
            gw_command = "sudo nmcli con modify " + gw_interface +" ipv4.gateway \"" + nat_address + "\" ; sudo systemctl restart network;"

        elif len(orderlist1) != 0 and len(orderlist2) != 0:
            nat_command = "sudo nmcli con modify " + nat_interface + " ipv4.routes \"" + service1_domain + " " + myOrderlist1[1] + "\" +ipv4.routes \"" + service2_domain + " " + myOrderlist2[1] + "\" ; sudo systemctl restart network;"
            gw_command = "sudo nmcli con modify " + gw_interface +" ipv4.gateway \"" + myOrderlist1[len(myOrderlist1)-2] + "\" ; sudo systemctl restart network;"
            if(flow1_order.fw_order != -1):
                fw_command = "sudo nmcli con modify " + fw_interface + " ipv4.routes \"" + service1_domain + " " + myOrderlist1[flow1_order.fw_order+1] + "\" +ipv4.routes \"" + service2_domain + " " + myOrderlist2[flow2_order.fw_order+1] + "\" ; sudo nmcli con modify " + fw_interface +" ipv4.gateway \"" + myOrderlist1[flow1_order.fw_order-1] + "\" ; sudo systemctl restart network;"
            if(flow1_order.ids_order != -1):
                ids_command = "sudo nmcli con modify " + ids_interface + " ipv4.routes \"" + service1_domain + " " + myOrderlist1[flow1_order.ids_order+1] + "\" +ipv4.routes \"" + service2_domain + " " + myOrderlist2[flow2_order.ids_order+1] +  "\" ; sudo nmcli con modify " + ids_interface +" ipv4.gateway \"" + myOrderlist1[flow1_order.ids_order-1] + "\" ; sudo systemctl restart network;"
            if(flow1_order.dpi_order != -1):
                dpi_command = "sudo nmcli con modify " + dpi_interface + " ipv4.routes \"" + service1_domain + " " + myOrderlist1[flow1_order.dpi_order+1] + "\" +ipv4.routes \"" + service2_domain + " " + myOrderlist2[flow2_order.dpi_order+1] + "\" ; sudo nmcli con modify " + dpi_interface +" ipv4.gateway \"" + myOrderlist1[flow1_order.dpi_order-1] + "\" ; sudo systemctl restart network;"
            if(flow1_order.waf_order != -1):
                waf_command = "sudo nmcli con modify " + waf_interface + " ipv4.routes \"" + service2_domain + " " + myOrderlist1[flow1_order.waf_order+1] + "\" +ipv4.routes \"" + service2_domain + " " + myOrderlist2[flow2_order.fw_order+1] + "\" ; sudo nmcli con modify " + waf_interface +" ipv4.gateway \"" + myOrderlist1[flow1_order.waf_order-1] + "\" ; sudo systemctl restart network;"

        elif len(orderlist1) != 0 and len(orderlist2) == 0:
            nat_command = "sudo nmcli con modify " + nat_interface + " ipv4.routes \"" + service1_domain + " " + myOrderlist1[1] + "\" +ipv4.routes \"" + service2_domain + " " + gw_address + "\" ; sudo systemctl restart network;"
            gw_command = "sudo nmcli con modify " + gw_interface +" ipv4.gateway \"" + myOrderlist1[len(myOrderlist1)-2] + "\" ; sudo systemctl restart network;"
            if(flow1_order.fw_order != -1):
                fw_command = "sudo nmcli con modify " + fw_interface + " ipv4.routes \"" + service1_domain + " " + myOrderlist1[flow1_order.fw_order+1] + "\" ; sudo nmcli con modify " + fw_interface +" ipv4.gateway \"" + myOrderlist1[flow1_order.fw_order-1] + "\" ; sudo systemctl restart network;"
            if(flow1_order.ids_order != -1):
                ids_command = "sudo nmcli con modify " + ids_interface + " ipv4.routes \"" + service1_domain + " " + myOrderlist1[flow1_order.ids_order+1] + "\" ; sudo nmcli con modify " + ids_interface +" ipv4.gateway \"" + myOrderlist1[flow1_order.ids_order-1] + "\" ; sudo systemctl restart network;"
            if(flow1_order.dpi_order != -1):
                dpi_command = "sudo nmcli con modify " + dpi_interface + " ipv4.routes \"" + service1_domain + " " + myOrderlist1[flow1_order.dpi_order+1] + "\" ; sudo nmcli con modify " + dpi_interface +" ipv4.gateway \"" + myOrderlist1[flow1_order.dpi_order-1] + "\" ; sudo systemctl restart network;"
            if(flow1_order.waf_order != -1):
                waf_command = "sudo nmcli con modify " + waf_interface + " ipv4.routes \"" + service2_domain + " " + myOrderlist1[flow1_order.waf_order+1] + "\" ; sudo nmcli con modify " + waf_interface +" ipv4.gateway \"" + myOrderlist1[flow1_order.waf_order-1] + "\" ; sudo systemctl restart network;"
        elif len(orderlist1) == 0 and len(orderlist2) != 0:
            nat_command = "sudo nmcli con modify " + nat_interface + " ipv4.routes \"" + service1_domain + " " + gw_address + "\" +ipv4.routes \"" + service2_domain + " " + myOrderlist2[1] + "\" ; sudo systemctl restart network;"
            gw_command = "sudo nmcli con modify " + gw_interface +" ipv4.gateway \"" + myOrderlist2[len(myOrderlist2)-2] + "\" ; sudo systemctl restart network;"
            if(flow2_order.fw_order != -1):
                fw_command = "sudo nmcli con modify " + fw_interface + " ipv4.routes \"" + service2_domain + " " + myOrderlist2[flow2_order.fw_order+1] + "\" ; sudo nmcli con modify " + fw_interface +" ipv4.gateway \"" + myOrderlist2[flow2_order.fw_order-1] + "\" ; sudo systemctl restart network;"
            if(flow2_order.ids_order != -1):
                ids_command = "sudo nmcli con modify " + ids_interface + " ipv4.routes \"" + service2_domain + " " + myOrderlist2[flow2_order.ids_order+1] + "\" ; sudo nmcli con modify " + ids_interface +" ipv4.gateway \"" + myOrderlist2[flow2_order.ids_order-1] + "\" ; sudo systemctl restart network;"
            if(flow2_order.dpi_order != -1):
                dpi_command = "sudo nmcli con modify " + dpi_interface + " ipv4.routes \"" + service2_domain + " " + myOrderlist2[flow2_order.dpi_order+1] + "\" ; sudo nmcli con modify " + dpi_interface +" ipv4.gateway \"" + myOrderlist2[flow2_order.dpi_order-1] + "\" ; sudo systemctl restart network;"
            if(flow2_order.waf_order != -1):
                waf_command = "sudo nmcli con modify " + waf_interface + " ipv4.routes \"" + service2_domain + " " + myOrderlist2[flow2_order.waf_order+1] + "\" ; sudo nmcli con modify " + waf_interface +" ipv4.gateway \"" + myOrderlist2[flow2_order.waf_order-1] + "\" ; sudo systemctl restart network;"
 
        fw_post_data = {"command":fw_command}
        fwr = {"status":"unknow"}        
        ids_post_data = {"command":ids_command}
        idsr = {"status":"unknow"}
        dpi_post_data = {"command":dpi_command}
        dpir = {"status":"unknow"}
        waf_post_data = {"command":waf_command}
        wafr = {"status":"unknow"}

        try :
            fwr = json.loads(requests.post("http://"+fwip+"/iptables/rt", fw_post_data, timeout=10).content.decode('utf-8'))
        except Exception as e:
            fwr = {"status":"false"}
        try :
            idsr = json.loads(requests.post("http://"+idsip+"/suricata/rt", ids_post_data, timeout=10).content.decode('utf-8'))
        except Exception as e:
            idsr = {"status":"false"}
        try :
            dpir = json.loads(requests.post("http://"+dpiip+"/ntopng/rt", dpi_post_data, timeout=10).content.decode('utf-8'))
        except Exception as e:
            dpir = {"status":"false"}
        try :
            wafr = json.loads(requests.post("http://"+wafip+"/modsec/rt", waf_post_data, timeout=10).content.decode('utf-8'))
        except Exception as e:
            wafr = {"status":"false"}

        nat_post_data = {"command":nat_command}
        natr = {"status":"unknow"}
        gw_post_data = {"command":gw_command}
        gwr = {"status":"unknow"}
        try :
            natr = json.loads(requests.post("http://"+natip+"/nat/rt", nat_post_data, timeout=10).content.decode('utf-8'))
        except Exception as e:
            natr = {"status":"false"}
        try :
            gwr = json.loads(requests.post("http://"+gwip+"/gw/rt", gw_post_data, timeout=10).content.decode('utf-8'))
        except Exception as e:
            gwr = {"status":"false"}

        nat_check_command = "traceroute "+gw_address2
        nat_check_post_data = {"command":nat_check_command}
        nat_check_r = {"order":"unknow"}
        try :
            nat_check_r = json.loads(requests.post("http://"+natip+"/nat/traceroute", nat_check_post_data, timeout=30).content.decode('utf-8'))
            nat_check_r['order'] = nat_check_r['order'].replace(fw_address,"FW").replace(ids_address,"IDS").replace(dpi_address,"DPI").replace(waf_address,"WAF").replace(gw_address2+">","").replace(">"+gw_address+">"+gw_address+">","")

        except Exception as e:
            nat_check_r = {"order":"false"}

    else:
        serviceorder = "尚未選擇網路安全服務鏈接執行順序"
    # return render(request,"SFC.html",{"result":nat_check_r['order']})#,"nat":nat_command,"fw":fw_command,"ids":ids_command,"dpi":dpi_command,"waf":waf_command,"gw":gw_command})

    return render(request,"SFC.html",{"serviceorder":orderlist1,"nat":nat_command,"fw":fw_command,"ids":ids_command,"dpi":dpi_command,"waf":waf_command,"gw":gw_command})

