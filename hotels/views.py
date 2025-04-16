from django.shortcuts import render, get_object_or_404, redirect
from .models import Place, Hotel
import folium
import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json
from .gemini_ai import generate_trip_plan
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages




# Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def hotel_details(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    # Create a Razorpay Order
    order_amount = int(hotel.price * 100)  # Convert price to paise
    order_currency = "INR"
    order = razorpay_client.order.create(
        {"amount": order_amount, "currency": order_currency, "payment_capture": "1"}
    )

    return render(request, 'hotels/hotel_details.html', {
        'hotel': hotel,
        'order_id': order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID
    })

@csrf_exempt
@login_required
def payment_success(request, hotel_id):
    """Handle successful payment and update user's travel history"""
    if request.method == 'POST':
        hotel = get_object_or_404(Hotel, id=hotel_id)
        user = request.user
        
        # Get payment details from POST data
        payment_id = request.POST.get('razorpay_payment_id', '')
        payment_status = 'completed'
        
        # Create booking details as JSON string
        import datetime
        booking_details = {
            "hotel_id": hotel.id,
            "hotel_name": hotel.name,
            "place_id": hotel.place.id,
            "place_name": hotel.place.name,
            "image": hotel.image.url if hotel.image else "",
            "booking_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "price": str(hotel.price),
            "payment_id": payment_id,
            "payment_status": payment_status
        }
        
        # Update user's travel history by adding the new booking
        if user.profile.travel_history:
            # Convert existing history to list, add new booking, convert back to string
            try:
                history_list = json.loads(user.profile.travel_history)
                if not isinstance(history_list, list):
                    history_list = [history_list]
            except:
                # If existing data is not valid JSON, start fresh
                history_list = []
            
            history_list.append(booking_details)
            user.profile.travel_history = json.dumps(history_list)
        else:
            # First booking
            user.profile.travel_history = json.dumps([booking_details])
        
        user.profile.save()
        
        messages.success(request, f'Booking confirmed for {hotel.name}!')
        return redirect('profile')
    
    return redirect('home')

@csrf_exempt
def generate_ai_trip(request):
    """API endpoint to generate trip plans with Gemini AI."""
    if request.method == 'POST':
        try:
            # Parse JSON data from request
            data = json.loads(request.body)
            destination_name = data.get('destination', {}).get('name', '')
            start_date = data.get('startDate', '')
            end_date = data.get('endDate', '')
            companions = data.get('companions', 'solo')
            activities = data.get('activities', [])
            
            # Convert companions code to descriptive text
            companions_map = {
                'solo': 'solo adventure',
                'partner': 'romantic getaway',
                'friends': 'trip with friends',
                'family': 'family vacation'
            }
            companions_text = companions_map.get(companions, companions)
            
            # Convert activity codes to descriptive text
            activity_map = {
                'beaches': 'beaches and relaxation',
                'hiking': 'hiking and nature exploration',
                'culture': 'cultural and historical experiences',
                'food': 'food and culinary exploration',
                'adventure': 'adventure and sports activities',
                'nightlife': 'nightlife and entertainment',
                'shopping': 'shopping and markets',
                'wellness': 'wellness and spa experiences'
            }
            
            activity_texts = [activity_map.get(act, act) for act in activities]
            
            # Generate AI trip plan
            trip_html = generate_trip_plan(
                destination_name, 
                start_date, 
                end_date, 
                companions_text, 
                activity_texts
            )
            
            return JsonResponse({
                'success': True,
                'tripHtml': trip_html
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Only POST requests are supported'}, status=405)

def Trip(request):
    return render(request, 'hotels/trip.html')

# Home Page - Displays all places
def home(request):
    places = Place.objects.all()
    return render(request, 'hotels/home.html', {'places': places})

# Place Details Page
def place_details(request, place_id):
    place = get_object_or_404(Place, id=place_id)

    # Create a map centered on the place
    m = folium.Map(location=[place.latitude, place.longitude], zoom_start=12)
    folium.Marker(
        location=[place.latitude, place.longitude],
        popup=place.name,
        tooltip=place.name,
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)
    
    map_html = m._repr_html_()
    
    return render(request, 'hotels/place_details.html', {'place': place, 'map_html': map_html})

# Hotels Near a Place
def hotels_near_place(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    hotels = place.hotels.all()

    # Create a map centered on the place
    m = folium.Map(location=[place.latitude, place.longitude], zoom_start=12)
    
    # Add markers for each hotel
    for hotel in hotels:
        folium.Marker(
            location=[hotel.latitude, hotel.longitude],
            popup=hotel.name,
            tooltip=hotel.name,
            icon=folium.Icon(color="blue"),
        ).add_to(m)

    map_html = m._repr_html_()

    return render(request, 'hotels/hotels_near_place.html', {'place': place, 'hotels': hotels, 'map_html': map_html})

# About Us Page
def about(request):
    """View for the About Us page"""
    return render(request, 'hotels/about.html')

# Contact Page
def contact(request):
    """View for the Contact page"""
    if request.method == 'POST':
        # Process contact form submission
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # You could add code here to send an email or save to database
        
        messages.success(request, "Thank you for your message! We'll get back to you soon.")
        return redirect('contact')
        
    return render(request, 'hotels/contact.html')
