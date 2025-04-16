import google.generativeai as genai
from django.conf import settings

def initialize_gemini():
    """Initialize the Gemini AI client with API key from settings."""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')

def generate_trip_plan(destination, start_date, end_date, companions, activities):
    """Generate a personalized trip plan using Gemini AI."""
    model = initialize_gemini()
    
    # Format activities for better prompt
    formatted_activities = ', '.join(activities)
    
    # Calculate trip duration
    from datetime import datetime
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    duration = (end - start).days
    
    # Create a detailed prompt for Gemini
    prompt = f"""
    Create a personalized {duration}-day trip itinerary for {destination} from {start_date} to {end_date}.
    This is a {companions} trip focusing on these activities: {formatted_activities}.
    
    Please include:
    1. A brief introduction to {destination} highlighting why it's perfect for this type of trip
    2. A day-by-day itinerary with clear Morning, Afternoon, and Evening sections for each day
    3. At least 3 specific attraction recommendations with brief descriptions
    4. 2-3 restaurant recommendations that match the traveler's interests
    5. 1-2 insider tips that most tourists might not know about
    
    Format the response in HTML with the following structure:
    - Use <h1> for the main title
    - Use <h2> for day headers like "Day 1" and section headers
    - Use <h3> for subsections
    - Use <p> for paragraphs
    - Use <ul> or <ol> for lists
    - Each day should have clear Morning, Afternoon, and Evening sections
    - Format restaurant names in bold
    - Prefix insider tips with "Tip: " for easy identification
    
    IMPORTANT: Make sure the content is detailed, specific to {destination}, and matches the travel preferences.
    """
    
    # Generate content
    response = model.generate_content(prompt)
    return response.text 