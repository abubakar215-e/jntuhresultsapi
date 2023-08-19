from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse
from asgiref.sync import sync_to_async
from jntuhresults.Executables import Search_by_Roll_number
from jntuhresults.Executables.constants import a_dic,Index_Keys
from jntuhresults.Executables.examcodes import get_exam_codes
from jntuhresults.Executables.notificationscraper import get_notifications
import json
import asyncio
import time
from django.views.generic import View
from django.http import JsonResponse
from jntuhresults.Executables.jntuhresultscraper import ResultScraper
import redis
import json
from datetime import timedelta
import os
from dotenv import load_dotenv


load_dotenv()
redis_url=os.environ.get("REDIS_URL")
redis_client = redis.from_url(redis_url)

listi=['1-1','1-2','2-1','2-2','3-1','3-2','4-1','4-2']
JNTUH_Results={}
#Page Not Found Redirect
def page_not_found_view(request, exception):
    return redirect('/api/single?htno=19361A0555')
    
def cors(request):
    return HttpResponse("hello")

# --------------------Semester Results ---------------------
class semresult(View):
    async def scrape_results_async(self, htno, code):
        # Create an instance of ResultScraper
        jntuhresult = ResultScraper(htno.upper())

        # Scrape the result asynchronously
        result = await jntuhresult.scrape_all_results(code)

        return result

    async def get(self, request):
        print(request.META.get("HTTP_USER_AGENT"))
        # Retrieve htno and semester from the GET parameters
        htno = request.GET.get('htno')
        code = request.GET.get('code')

        # Print htno for debugging
        # print(htno)

        # Scrape the result asynchronously
        result = await self.scrape_results_async(htno, code)

        # Check if the result is empty
        if not result["Details"]:
           return HttpResponse("Internal Server Error ", status=500)
        print(htno,result['Details']['NAME'])

        # Return the result as a JSON response
        return JsonResponse(result, safe=False)




# ----------------------------------------------------------------

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
# ---------------------------------------------------


# ------------------Notifications-------------------
def notify(request):
    notifications = get_notifications()
    return JsonResponse(notifications, safe=False)


#------------------------------------------testing area danger-------
def homepage(request):
    return render(request,'index.html')

# ----------------------------------------------------
#academicresult------------------------------------------------------------------------------------------------------------

class AcademicResult(View):
    def get(self,request):
        print(request.META.get("HTTP_USER_AGENT"))
        # Record the current time as the starting time
        starting =time.time()

        # Get the 'htno' parameter from the request and convert it to uppercase
        htno=request.GET.get('htno').upper()

        # Retrieve data from Redis cache using the 'htno' as the key
        redis_response = redis_client.get(htno)
        
        # Check if data exists in the Redis cache
        if redis_response is not None:
            # If data exists, parse the JSON response
            data = json.loads(redis_response)

            # Record the current time as the stopping time
            stopping=time.time()

            # Print relevant details (e.g., 'htno', student name, and execution time)
            print(htno,data["data"]['Details']['NAME'],stopping-starting)

            # Return the data as a JSON response to the client
            return JsonResponse(data["data"],safe=False)
        
        # Check if the hall ticket number is valid
        if len(htno) != 10:
            return HttpResponse(htno+" Invalid hall ticket number")
        try:
            # Create an instance of ResultScraper
            jntuhresult = ResultScraper(htno.upper())

            # Run the scraper and return the result
            result = jntuhresult.run()
                
            # Calculate the total marks and credits
            total_credits = 0  # Variable to store the total credits
            total = 0  # Variable to store the total marks
            failed = False  # Flag to indicate if any value is missing 'total' key

            # Iterate over the values in result["Results"] dictionary
            for value in result["Results"].values():
                if 'total' in value.keys():  # Check if the current value has 'total' key
                    total += value['total']  # Add the 'total' value to the total marks
                    total_credits += value['credits']  # Add the 'credits' value to the total credits
                else:
                    failed = True  # Set the flag to indicate missing 'total' key

            # Calculate the CGPA if there are non-zero credits
            if not failed:
                result["Results"]["Total"] = "{0:.2f}".format(round(total/total_credits,2))
            
            # Record the current time as the stopping time
            stopping=time.time()

            # Print relevant details (e.g., 'htno', student name, and execution time)
            print(htno,result['Details']['NAME'],stopping-starting)

            # Delete the variable 'jntuhresult' from memory
            del jntuhresult

          # Store the 'result' data in the Redis cache with the 'htno' as the key.
            try:
                redis_client.set(htno, json.dumps({"data": result}))
                
                # Set an expiration time of 6 hours for the cached data associated with 'htno'.
                redis_client.expire(htno, timedelta(hours=6))
                
                print("Data has been set in the Redis cache.")
            except Exception as e:
                print("Error setting data in the Redis cache:", e)

            # Return the result
            return JsonResponse(result,safe=False)
        
        except Exception as e:
            print(htno,e)
            # Catch any exceptions raised during scraping
            return HttpResponse(htno+" - 500 Internal Server Error")
           
#------------------------------------------------------------------------------------------------------------------


# Class Result ----------------------------------------------------------------------
class ClassResult(View):
    async def scrape_results_async(self, htno, semester):
        # Create an instance of ResultScraper
        jntuhresult = ResultScraper(htno.upper())

        # Scrape all the results asynchronously
        result = await jntuhresult.scrape_all_results(semester)

        return result

    async def get(self, request):
        # Retrieve htnos and semester from the GET parameters
        htnos = request.GET.get('htnos').split(",")
        semester = request.GET.get('semester')

        # Print htnos for debugging
        print(htnos)

        # Create a list to hold the tasks
        tasks = []

        # Add the tasks to the list
        for htno in htnos:
            # Create a task for scraping results asynchronously for each htno
            task = asyncio.create_task(self.scrape_results_async(htno, semester))
            tasks.append(task)

        # Await all the tasks to complete
        gathered_results = await asyncio.gather(*tasks)

        # Filter out the empty results
        filtered_results = [result for result in gathered_results if result["Details"]]

        # Return the results as a JSON response
        return JsonResponse(filtered_results, safe=False)


# ------------------------------------------------------------------------------
# -----------------overallresults-------
class ClassResults(View):
    async def scrape_results_async(self, htno):
        # Create an instance of ResultScraper
        jntuhresult = ResultScraper(htno.upper())

        # Scrape all the results
        result = jntuhresult.run()

        # Check if the result has valid data
        if "Details" not in result or not result["Details"]:
            # Return None if the result is empty or does not have "Details"
            return None

        # Calculate the total marks and credits
        total_credits = 0  # Variable to store the total credits
        total = 0  # Variable to store the total marks
        failed = False  # Flag to indicate if any value is missing 'total' key

        # Iterate over the values in result["Results"] dictionary
        for value in result["Results"].values():
            if 'total' in value.keys():  # Check if the current value has 'total' key
                total += value['total']  # Add the 'total' value to the total marks
                total_credits += value['credits']  # Add the 'credits' value to the total credits
            else:
                failed = True  # Set the flag to indicate missing 'total' key

        # Calculate the CGPA if there are non-zero credits
        if not failed:
            result["Results"]["Total"] = "{0:.2f}".format(round(total / total_credits, 2))

        stopping = time.time()
        print(htno, result['Details']['NAME'])

        return result

    async def get(self, request):
        # Retrieve htnos from the GET parameters
        htnos = request.GET.get('htnos').split(",")

        # Print htnos for debugging
        print(htnos)

        # Create a list to hold the tasks
        tasks = []

        # Add the tasks to the list
        for htno in htnos:
            # Create a task for scraping results asynchronously for each htno
            task = asyncio.create_task(self.scrape_results_async(htno))
            tasks.append(task)

        # Await all the tasks to complete
        gathered_results = await asyncio.gather(*tasks)

        # Filter out the empty results
        filtered_results = [result for result in gathered_results if result is not None]

        # Return the results as a JSON response
        return JsonResponse(filtered_results, safe=False)
