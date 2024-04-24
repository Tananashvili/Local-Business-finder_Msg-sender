import googlemaps
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

API_KEY = "AIzaSyCM-KG8n3b9fhngC6cSXPiFcccesql-0RQ"
gmaps = googlemaps.Client(key=API_KEY)

def find_socials_on_website(website_url, social):
    paths_to_try = ["", "contact", "contacts", "contactus", "en/contact", "en/contacts", "en/contactus"]

    for path in paths_to_try:
        try_url = website_url + path
        response = requests.get(try_url, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = soup.find_all('a')

            if all_links:
                for link in all_links:
                    href = link.get('href')
                    if href and social in href:
                        return href

    return f"Couldn't find {social} on website."


def get_all_socials():
    excel_file = 'companies_info.xlsx'
    df = pd.read_excel(excel_file)
    df_len = df.shape[0]

    fbs_found = []
    instas_found = []
    i = 1
    for index, row in df.iterrows():
        website_url = row['website']

        if isinstance(website_url, str) and "facebook" in website_url:
            fbs_found.append(website_url)
            instas_found.append("Couldn't find Instagram")

        elif isinstance(website_url, str) and "instagram" in website_url:
            fbs_found.append("Couldn't find Facebook")
            instas_found.append(website_url)

        else:  
            try:
                response = requests.get(website_url, timeout=5)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    all_links = soup.find_all('a')

                    insta_found = False
                    fb_found = False

                    if all_links:
                        for link in all_links:
                            href = link.get('href')

                            if href and "facebook" in href:
                                fbs_found.append(href)
                                fb_found = True
                                i+=1
                                break

                            if href and "instagram" in href:
                                instas_found.append(href)
                                insta_found = True
                                i+=1
                                break

                    else:
                        fb = find_socials_on_website(website_url, "facebook")
                        fbs_found.append(fb)
                        fb_found = True

                        insta = find_socials_on_website(website_url, "instagram")
                        instas_found.append(insta)
                        insta_found = True
                    

                    if not fb_found:
                        fbs_found.append("Couldn't find Facebook")
                    if not insta_found:
                        instas_found.append("Couldn't find Instagram")

                else:
                    fbs_found.append("Couldn't open website.")
                    instas_found.append("Couldn't open website.")

            except Exception as e:
                fbs_found.append("Error while processing website.")
                instas_found.append("Error while processing website.")

            print(f"Fetching Socials {i}/{df_len}")
            i+=1

    fbs_found = [e.strip() if e is not None else e for e in fbs_found]
    df['facebook'] = fbs_found

    instas_found = [e.strip() if e is not None else e for e in instas_found]
    df['instagram'] = instas_found

    return df


def display_place_details(place_id, bus_type, location):
    place_details = gmaps.place(place_id=place_id)
    result = place_details.get("result", {})
    
    print(f"Name: {result.get('name', 'N/A')}")
    print(f"Address: {result.get('formatted_address', 'N/A')}")
    print(f"Phone Number: {result.get('formatted_phone_number', 'N/A')}")
    print(f"International Phone Number: {result.get('international_phone_number', 'N/A')}")
    print(f"Website: {result.get('website', 'N/A')}")
    print(f"Rating: {result.get('rating', 'N/A')}")
    print(f"Total Reviews: {result.get('user_ratings_total', 'N/A')}\n")

    return {"name": result.get('name', 'N/A'), "business_type": bus_type, "location": location, "website": result.get('website', 'N/A'), "address": result.get('formatted_address', 'N/A'), "number": result.get('formatted_phone_number', 'N/A'),
            'int_number': result.get('international_phone_number', 'N/A'), 'rating': result.get('rating', 'N/A'), 'reviews': result.get('user_ratings_total', 'N/A')}

COMPANIES = []
# Function to search for the place and display results
def search_and_display_places(query, lat_lng, loc, page_token=None):
    attempts = 0
    result = None

    while attempts < 5:
        try:
            result = gmaps.places(
                query=query,
                location=lat_lng,
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
            company = display_place_details(item["place_id"], query, loc)
            COMPANIES.append(company)

        # Check if there's a next page token
        next_page_token = result.get("next_page_token")
        if next_page_token:
            search_and_display_places(query, location, loc, next_page_token)


df = pd.read_excel("input_data.xlsx")

for index, row in df.iterrows():
    business_type = row['business']
    location = row['location']
    
    geocode_result = gmaps.geocode(location)
    if geocode_result:
        loc = geocode_result[0]["geometry"]["location"]
        lat = loc["lat"]
        lng = loc["lng"]

        search_and_display_places(business_type, (lat, lng), location)

    else:
        print("Location not found. Please check your input.")

companies = pd.DataFrame(COMPANIES)
companies.drop_duplicates(subset='website', keep='first', inplace=True)
companies.reset_index(drop=True, inplace=True)
companies.to_excel("companies_info.xlsx", index=False)

print("GETTING SOCIALS \n ____________________")

socials = get_all_socials()
socials.to_excel("output.xlsx", index=False)