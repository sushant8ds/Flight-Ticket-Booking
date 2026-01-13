"""
MongoDB-enabled views for Django Flight Booking Application
"""
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
import math

# Import MongoDB utilities
from .mongodb_utils import (
    connect_mongodb, get_places, search_places, get_flights, 
    get_flight_by_id, create_ticket, get_ticket_by_ref, 
    update_ticket_status, get_database_stats
)

# Import original models for user authentication (still using SQLite)
from .models import User

# Fee constant
FEE = 100.0

def index(request):
    """Home page with flight search"""
    min_date = f"{datetime.now().date().year}-{datetime.now().date().month}-{datetime.now().date().day}"
    max_date = f"{datetime.now().date().year if (datetime.now().date().month+3)<=12 else datetime.now().date().year+1}-{(datetime.now().date().month + 3) if (datetime.now().date().month+3)<=12 else (datetime.now().date().month+3-12)}-{datetime.now().date().day}"
    
    if request.method == 'POST':
        origin = request.POST.get('Origin')
        destination = request.POST.get('Destination')
        depart_date = request.POST.get('DepartDate')
        seat = request.POST.get('SeatClass')
        trip_type = request.POST.get('TripType')
        
        if trip_type == '1':
            return render(request, 'flight/index.html', {
                'origin': origin,
                'destination': destination,
                'depart_date': depart_date,
                'seat': seat.lower(),
                'trip_type': trip_type
            })
        elif trip_type == '2':
            return_date = request.POST.get('ReturnDate')
            return render(request, 'flight/index.html', {
                'min_date': min_date,
                'max_date': max_date,
                'origin': origin,
                'destination': destination,
                'depart_date': depart_date,
                'seat': seat.lower(),
                'trip_type': trip_type,
                'return_date': return_date
            })
    else:
        return render(request, 'flight/index.html', {
            'min_date': min_date,
            'max_date': max_date
        })

def login_view(request):
    """User login (still using SQLite for user auth)"""
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "flight/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "flight/login.html")

def register_view(request):
    """User registration (still using SQLite for user auth)"""
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        
        if password != confirmation:
            return render(request, "flight/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            user.save()
        except:
            return render(request, "flight/register.html", {
                "message": "Username already taken."
            })
        
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "flight/register.html")

def logout_view(request):
    """User logout"""
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def query(request, q):
    """Search places using MongoDB"""
    try:
        places = search_places(q)
        results = []
        for place in places:
            results.append({
                'code': place.code,
                'city': place.city,
                'country': place.country
            })
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)

@csrf_exempt
def flight(request):
    """Flight search using MongoDB"""
    try:
        o_place = request.GET.get('Origin')
        d_place = request.GET.get('Destination')
        trip_type = request.GET.get('TripType')
        departdate = request.GET.get('DepartDate')
        depart_date = datetime.strptime(departdate, "%Y-%m-%d")
        seat = request.GET.get('SeatClass')

        # Get flights from MongoDB
        flights = get_flights(o_place, d_place, depart_date.weekday(), seat)
        
        # Convert to list for template
        flight_list = []
        for flight in flights:
            flight_data = {
                'id': str(flight.id),
                'airline': flight.airline,
                'plane': flight.plane,
                'origin': {
                    'code': flight.origin.code,
                    'city': flight.origin.city,
                    'country': flight.origin.country
                },
                'destination': {
                    'code': flight.destination.code,
                    'city': flight.destination.city,
                    'country': flight.destination.country
                },
                'depart_time': flight.depart_time,
                'arrival_time': flight.arrival_time,
                'duration': flight.duration,
                'economy_fare': flight.economy_fare,
                'business_fare': flight.business_fare,
                'first_fare': flight.first_fare
            }
            flight_list.append(flight_data)

        # Calculate price range
        if flight_list:
            if seat == 'economy':
                fares = [f['economy_fare'] for f in flight_list if f['economy_fare'] > 0]
            elif seat == 'business':
                fares = [f['business_fare'] for f in flight_list if f['business_fare'] > 0]
            elif seat == 'first':
                fares = [f['first_fare'] for f in flight_list if f['first_fare'] > 0]
            
            if fares:
                max_price = math.ceil(max(fares)/100)*100
                min_price = math.floor(min(fares)/100)*100
            else:
                max_price = min_price = 0
        else:
            max_price = min_price = 0

        return render(request, "flight/search.html", {
            'flights': flight_list,
            'origin': {'code': o_place, 'city': o_place},
            'destination': {'code': d_place, 'city': d_place},
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'max_price': max_price,
            'min_price': min_price
        })
        
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def mongodb_stats(request):
    """Display MongoDB statistics"""
    try:
        stats = get_database_stats()
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)})

# Add other views as needed...
def contact(request):
    return render(request, 'flight/contact.html')

def privacy_policy(request):
    return render(request, 'flight/privacy-policy.html')

def terms_and_conditions(request):
    return render(request, 'flight/terms.html')

def about_us(request):
    return render(request, 'flight/about.html')