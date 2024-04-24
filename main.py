import googlemaps
import time
import pandas as pd
import random
from emails import get_all_emails, send_email

# Set up your Google API key
API_KEY = ""
gmaps = googlemaps.Client(key=API_KEY)

print("BUSINESS SEARCH \n")

# Inputs for location and business type
location = input("Enter the location: ")
business_type = input("Enter the business type: ")

# Function to display place details
def display_place_details(place_id):
    place_details = gmaps.place(place_id=place_id)
    result = place_details.get("result", {})
    
    print(f"Name: {result.get('name', 'N/A')}")
    print(f"Address: {result.get('formatted_address', 'N/A')}")
    print(f"Phone Number: {result.get('formatted_phone_number', 'N/A')}")
    print(f"International Phone Number: {result.get('international_phone_number', 'N/A')}")
    print(f"Website: {result.get('website', 'N/A')}")
    print(f"Rating: {result.get('rating', 'N/A')}")
    print(f"Total Reviews: {result.get('user_ratings_total', 'N/A')}\n")

    return {"name": result.get('name', 'N/A'), "website": result.get('website', 'N/A'), "address": result.get('formatted_address', 'N/A'), "number": result.get('formatted_phone_number', 'N/A'),
            'int_number': result.get('international_phone_number', 'N/A'), 'rating': result.get('rating', 'N/A'), 'reviews': result.get('user_ratings_total', 'N/A')}

COMPANIES = []
# Function to search for the place and display results
def search_and_display_places(query, location, page_token=None):
    attempts = 0
    result = None

    while attempts < 5:
        try:
            result = gmaps.places(
                query=query,
                location=location,
                radius=10000,
                page_token=page_token
            )

            if result["status"] == "INVALID_REQUEST" and page_token is not None:
                time.sleep(1)
                attempts += 1
                continue
            else:
                break
        except Exception as e:
            print(f"Error: {str(e)}")
            return

    if result and result["status"] == "OK":       
        for item in result["results"]:
            company = display_place_details(item["place_id"])
            COMPANIES.append(company)

        # Check if there's a next page token
        next_page_token = result.get("next_page_token")
        if next_page_token:
            search_and_display_places(query, location, next_page_token)

    companies = pd.DataFrame(COMPANIES)
    companies.drop_duplicates(subset='website', keep='first', inplace=True)
    companies.reset_index(drop=True, inplace=True)
    companies.to_excel("database.xlsx", index=False)

def send_emails(emails):
    print("INPUT DATA TO SEND EMAILS")

    your_email_address = input("Input Your Email Address: ")
    your_email_password = input("Input Your Email Password: ")
    subject = input("Subject: ")
    html_route = input("Name of the HTML Body File: ")
    attachment_name = input(f"Name of the Attachment File \n(input 0 if there is no attachment): ")
    from_ = input("from: ")

    with open(f"{html_route}.html", "r") as html_file:
        html_content = html_file.read()

    i = 1
    unique_emails = list(set(emails))
    for to_email in unique_emails:
        send_email(your_email_address, your_email_password, to_email, subject, html_content, attachment_name, from_)
        print(f"Email Sent Successfully {i}/{unique_emails}")
        
        random_wait_time = random.uniform(1, 4)
        time.sleep(random_wait_time)
        i += 1

if location and business_type:
    # Geocoding an address
    geocode_result = gmaps.geocode(location)

    if geocode_result:
        loc = geocode_result[0]["geometry"]["location"]
        lat = loc["lat"]
        lng = loc["lng"]

        # Search for the place and display results
        search_and_display_places(business_type, (lat, lng))

    else:
        print("Location not found. Please check your input.")
else:
    print("Please enter both location and business type.")

get_emails_str = input("Get Emails? (y/n): ")

if get_emails_str == "y":
    emails = get_all_emails(location, business_type)
    print(f"{len(emails)} Emails Found. \n")
    send_emails(emails)
