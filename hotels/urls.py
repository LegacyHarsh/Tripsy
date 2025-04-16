from django.urls import path
from .views import home, place_details, hotels_near_place,hotel_details,Trip, generate_ai_trip, payment_success, about, contact

urlpatterns = [
    path('', home, name='home'),
    path('trip/', Trip, name='trip'),
    path('place/<int:place_id>/', place_details, name='place_details'),
    path('place/<int:place_id>/hotels/', hotels_near_place, name='hotels_near_place'),
    path('hotel/<int:hotel_id>/', hotel_details, name='hotel_details'),
    path('hotel/<int:hotel_id>/payment-success/', payment_success, name='payment_success'),
    path('generate-ai-trip/', generate_ai_trip, name='generate_ai_trip'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
]
