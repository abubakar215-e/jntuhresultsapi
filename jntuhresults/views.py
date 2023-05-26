from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse
from asgiref.sync import sync_to_async
from jntuhresults.Executables import Search_by_Roll_number
from jntuhresults.Executables.constants import a_dic,Index_Keys
from jntuhresults.Executables.examcodes import get_exam_codes
import json
import asyncio
import time
from django.views.generic import View
from django.http import JsonResponse


listi=['1-1','1-2','2-1','2-2','3-1','3-2','4-1','4-2']
JNTUH_Results={}
#Page Not Found Redirect
def page_not_found_view(request, exception):
    return redirect('/api/single?htno=19361A0555')
    
def cors(request):
    return HttpResponse("hello")
#Multi-----------------------------------------------------------------------------------------------------
class multi(View):
    async def gettingurl(self,htno,fro,to,code):
        tasksi=[]
        First_Index,Last_Index=Index_Keys.index(fro),Index_Keys.index(to)
        Index_List=Index_Keys[First_Index:Last_Index+1]
        for i in Index_List:
            Result=Search_by_Roll_number.Results()
            tasksi.append(asyncio.create_task(Result.getting_faster_Grades(htno+i,code)))
        responses = asyncio.gather(*tasksi)
        return await responses

    def get(self,request):
        global listi
        try:
            htno1=request.GET.get('from').upper()
            htno2=request.GET.get('to').upper()
            code=request.GET.get('code').upper()
        except:
            return HttpResponse("Pass from and to roll number as query")
        if(code not in listi):
            return HttpResponse("Please put down the correct code")
        if(htno1[:8]!=htno2[:8]):
            return HttpResponse("Please Maintain from roll number first and last numbers as same")
        elif(htno1[8:]>htno2[8:]):
            return HttpResponse("First Hall ticket should be greater")
        elif(len(htno1)!=10 or len(htno2)!=10):
            return HttpResponse("Please Enter the Roll Numbers correctly")
        res=asyncio.run(self.gettingurl(htno1[:8],htno1[8:],htno2[8:],code))
        response=list()
        for i in res:
            if(len(i['Results'][code])==0):
                del i   
            else:
                response.append(i)
        return JsonResponse(response,safe=False)
#----------------------------------------------------------------------------------------------------------------



#single------------------------------------------------------------------------------------------------------------
class allResults(View):
    async def allResults_extend(self,htno):
            global listi
            listE=listi
            if(htno[4]=='5'):
                listE=listi[2:]
            tasksi=[]
            for i in listE:
                Result=Search_by_Roll_number.Results()
                tasksi.append(asyncio.create_task(Result.getting_faster_Grades(htno,i)))
            responses = asyncio.gather(*tasksi)
            return await responses

    #API for getting all Results
    def get(self,request):
        print(request.META.get("HTTP_USER_AGENT"))
        starting =time.time()
        try:
            htno=request.GET.get('htno').upper()
            print(htno)
        except:
            return HttpResponse('Enter hallticket number correctly')
        try:
            Result=JNTUH_Results[htno]
            stopping=time.time()
            print(stopping-starting)
            print("Loaded from cache")
            return JsonResponse(Result,safe=False)
        except:
            print("Not loaded from cache")
        try:
            json_object = asyncio.run(self.allResults_extend(htno))
        except:
            print("Failed")
            return HttpResponse("Not working correctly",status=400)
        Results={}
        Results['Details']={}
        Results['Results']={}
        total=0
        credits=0
        all_pass=True
        for i in json_object:   
            try:
                for ind in i['Results']:
                    Results['Results'][ind]=i['Results'][ind]
                    Results['Details']=i['DETAILS']
                    try:
                        total=total+i['Results'][ind]['total']
                        credits=credits+i['Results'][ind]['credits']
                    except:
                        all_pass=False
            except:
                del Results['Results'][ind]
        try:
            print(Results['Details']['NAME'])
        except:
            pass
        if(all_pass):
            Results['Results']['Total']="{0:.2f}".format(round(total/credits,2))
        stopping=time.time()
        print(stopping-starting)
        # JNTUH_Results[htno]=Results
        return JsonResponse(Results,safe=False)
#------------------------------------------------------------------------------------------------------------------

#---------------------results of each sem---------------------------------------

class result(View):
    async def gettingurl(self, htno, code):
        tasksi=[]
        Result=Search_by_Roll_number.Results()
        tasksi.append(asyncio.create_task(Result.getting_faster_Grades(htno,code)))
        responses = asyncio.gather(*tasksi)
        return await responses

    def get(self,request):
        global listi
        try:
            htno=request.GET.get('htno').upper()
            if not htno:
                raise ValueError("HTNO parameter is missing or empty.")
            code=request.GET.get('code').upper()
            if not code:
                raise ValueError("Code parameter is missing or empty.")
        except ValueError as ve:
            return HttpResponse(f"Error: {ve}")
        
        if(code not in listi):
            return HttpResponse("Please put down the correct code")
        if(len(htno)!=10):
            return HttpResponse("Please enter a valid htno")
        
        try:
            res=asyncio.run(self.gettingurl(htno, code))
        except Exception as e:
            return HttpResponse(f"Error: {e}")
        
        response=list()
        for i in res:
            if(len(i['Results'][code])==0):
                del i   
            else:
                response.append(i)
        return JsonResponse(response,safe=False)




        # -------------------------------------------------------------



class cMode(View):
    async def allResults_extend(self, htno):
        global listi
        listE = listi
        if (htno[4] == '5'):
            listE = listi[2:]
        tasksi = []
        for i in listE:
            Result = Search_by_Roll_number.Results()
            tasksi.append(asyncio.create_task(Result.getting_faster_Grades(htno, i)))
        responses = asyncio.gather(*tasksi)
        return await responses

    # API for getting all Results
    def get(self, request):
        starting = time.time()
        try:
            htno1 = request.GET.get('htno1').upper()
            htno2 = request.GET.get('htno2').upper()
            print(htno1)
            print(htno2)
        except:
            return HttpResponse('Enter hallticket number correctly')
        try:
            Result1 = JNTUH_Results[htno1]
            Result2 = JNTUH_Results[htno2]
            stopping = time.time()
            print(stopping - starting)
            print("Loaded from cache")
            return JsonResponse({'Result1': Result1, 'Result2': Result2}, safe=False)
        except:
            print("Not loaded from cache")
        try:
            json_object1 = asyncio.run(self.allResults_extend(htno1))
            json_object2 = asyncio.run(self.allResults_extend(htno2))
        except:
            print("Failed")
            return HttpResponse("Not working correctly", status=400)
        Results1 = {}
        Results1['Details'] = {}
        Results1['Results'] = {}
        total1 = 0
        credits1 = 0
        all_pass1 = True
        for i in json_object1:   
            try:
                for ind in i['Results']:
                    Results1['Results'][ind] = i['Results'][ind]
                    Results1['Details'] = i['DETAILS']
                    try:
                        total1 = total1 + i['Results'][ind]['total']
                        credits1 = credits1 + i['Results'][ind]['credits']
                    except:
                        all_pass1 = False
            except:
                del Results1['Results'][ind]
        try:
            print(Results1['Details']['NAME'])
        except:
            pass
        if (all_pass1):
            Results1['Results']['Total'] = "{0:.2f}".format(round(total1 / credits1, 2))
        Results2 = {}
        Results2['Details'] = {}
        Results2['Results'] = {}
        total2 = 0
        credits2 = 0
        all_pass2 = True
        for i in json_object2:   
            try:
                for ind in i['Results']:
                    Results2['Results'][ind] = i['Results'][ind]
                    Results2['Details'] = i['DETAILS']
                    try:
                        total2 = total2 + i['Results'][ind]['total']
                        credits2 = credits2 + i['Results'][ind]['credits']
                    except:
                        all_pass2 = False
            except:
                del Results2['Results'][ind]
        try:
            print(Results2['Details']['NAME'])
        except:
            pass
        if (all_pass2):
            Results2['Results']['Total'] = "{0:.2f}".format(round(total2 / credits2, 2))
        stopping = time.time()
        print(stopping - starting)
        # JNTUH_Results[htno] = Results
        return JsonResponse({'Result1': Results1, 'Result2': Results2}, safe=False)


# ----------------------------------------------------------------- 




#examcode---------------------------------------
def exam_codes_api(request):
    exam_codes = get_exam_codes()
    return JsonResponse(exam_codes)

#------------------------------------------testing area danger-------
