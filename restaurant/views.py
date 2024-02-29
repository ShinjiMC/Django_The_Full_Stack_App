# from django.http import HttpResponse
from django.shortcuts import render
from .forms import BookingForm
from .models import Menu
from django.core import serializers
from .models import Booking
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime

def format_time(time_slot):
    hour = time_slot
    am_pm = "AM" if hour < 12 else "PM"
    formatted_hour = hour if hour < 12 else hour - 12 
    return f"{formatted_hour} {am_pm}"


# Create your views here.
def home(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def reservations(request):
    date_str = request.GET.get("date", datetime.today().strftime("%Y-%m-%d"))
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # Filtra las reservas por la fecha y las ordena por fecha y hora de reserva
    bookings = Booking.objects.filter(reservation_date=date).order_by('reservation_date', 'reservation_slot')
    formatted_bookings = []
    
    for booking in bookings:
        formatted_booking = {
            "first_name": booking.first_name,
            "reservation_date": booking.reservation_date.strftime("%Y-%m-%d"),
            "reservation_slot": format_time(booking.reservation_slot),  # Asumiendo que reservation_slot ya es un objeto datetime.time
        }
        formatted_bookings.append(formatted_booking)

    return render(request, "bookings.html", {"bookings": formatted_bookings})


def book(request):
    form = BookingForm()
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {"form": form}
    return render(request, "book.html", context)


# Add your code here to create new views
def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, "menu.html", {"menu": main_data})


def display_menu_item(request, pk=None):
    if pk:
        menu_item = Menu.objects.get(pk=pk)
    else:
        menu_item = ""
    return render(request, "menu_item.html", {"menu_item": menu_item})


@csrf_exempt
def bookings(request):
    if request.method == "POST":
        data = json.loads(request.body)
        exist = Booking.objects.filter(reservation_date=data["reservation_date"], reservation_slot=data["reservation_slot"]).exists()
        if not exist:
            booking = Booking(
                first_name=data["first_name"],
                reservation_date=data["reservation_date"],
                reservation_slot=data["reservation_slot"],
            )
            booking.save()
            # Retorna una respuesta de éxito con la información del booking creado.
            return JsonResponse({"success": True, "message": "Booking successfully created."})
        else:
            # Retorna una respuesta de error indicando que el slot ya está reservado.
            return JsonResponse({"error": True, "message": "This slot is already booked."}, status=400)

    # Manejo de GET request para obtener los bookings de una fecha específica.
    date = request.GET.get("date", datetime.today().date())
    bookings = Booking.objects.filter(reservation_date=date)
    booking_json = serializers.serialize("json", bookings)
    return HttpResponse(booking_json, content_type="application/json")
