import streamlit as st
import re
from PIL import Image
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Set page title and icon
import json
import time
# if st.button("Analysis"):
st.title("Pros and Cons of Jamf")

# Pros
st.markdown("### Pros of Jamf")
st.markdown("""
- **Robust Apple Device Management**: Jamf excels in managing Apple ecosystems. It allows for seamless deployment, configuration, and security across Macs, iPads, iPhones, and Apple TVs.
- **Ease of Use**: Its user interface is intuitive, and it’s easy to set up and manage devices. This reduces the learning curve for IT teams.
- **Automated Device Enrollment**: Jamf integrates directly with Apple’s Device Enrollment Program (DEP), allowing devices to be automatically configured and ready for use straight out of the box.
- **Comprehensive Security Management**: Jamf provides excellent control over security policies, patch management, and encryption, ensuring that devices stay compliant and secure.
- **Custom Scripting Support**: For more advanced IT teams, Jamf allows custom scripting, which means you can push custom commands and workflows across devices.
- **Integration with other SaaS Tools**: Jamf integrates with various other software, such as Microsoft Azure AD, Google Workspace, and other identity management solutions, making it easier to manage users and devices at scale.
""")

# Cons
st.markdown("### Cons of Jamf")
st.markdown("""
- **Cost**: Jamf can be expensive, especially for smaller organizations or those with fewer Apple devices. Its pricing structure is per device, which can add up quickly.
- **Complexity for Small Teams**: While Jamf offers powerful tools, many features may be overkill for smaller businesses that don't need such detailed management of their Apple devices.
- **Limited to Apple Ecosystem**: Jamf’s core strength is its deep integration with Apple products, but if your organization uses a mixed ecosystem (Windows, Android), Jamf’s usefulness is limited.
- **Requires Expertise for Advanced Features**: While it’s easy to get started, fully leveraging Jamf’s capabilities requires IT staff with specialized knowledge, especially when dealing with custom scripts and automations.
- **Occasional Delays with Feature Updates**: Some users report that updates for new Apple OS releases and features can take time to implement, meaning that Jamf might lag slightly behind when supporting the latest Apple functionalities.
""")
API_URL = "https://app.reviewflowz.com/api/v2/accounts/1900/listings"
LISTINGS_API_URL = "https://app.reviewflowz.com/api/v2/accounts/1900/listings?count=10000"
AUTH_TOKEN = "biebfR5mWeg36dVubbTUGEx5"  # Replace with your actual token
# Streamlit app setup
st.markdown('<h1>Software Reviews</h1>', unsafe_allow_html=True)

# Input fields for the user
software_name = 'Jamf Products'
platform = 'G2'
# base_url = "https://www.g2.com/products/{software}/reviews"
# exp_site_url = base_url.format(software=software_name)
site_url= "https://www.g2.com/products/jamf-products/reviews"


# Function to make API request and extract the ID
def create_listing(software_name, platform, site_url):
    headers = {
        "accept": "*/*",
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "profile_name": software_name,
        "url": site_url,
        "platform": platform,
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        # Assuming the response contains JSON data with a 'profile_id' field
        response_data = response.json()  # Get the JSON response
        profile_id = response_data.get("profile_id", None)  # Extract 'profile_id'
        return profile_id, response.status_code
    else:
        return None, response.status_code


# Function to get all listings
def get_listings(auth_token):
    headers = { 
        "accept": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

    response = requests.get(LISTINGS_API_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        st.error(f"Failed to fetch listings. Status Code: {response.status_code}")
        return None

# Function to get account id    
def get_account_id(listing,have_id):
    for i in range(len(listing['data'])):
        if listing['data'][i]['platform']==platform and listing['data'][i]['profile_name'].lower()==software_name.lower():
            have_id=1
            # st.write(listing['data'][i]['id'])
            return have_id,listing['data'][i]['id']
    return 0,0
    
# Function to fetch the review
def fetch_review(platform, token_number):
    api_url = "https://app.reviewflowz.com/api/v2/accounts/1900/reviews"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer biebfR5mWeg36dVubbTUGEx5"  
    }
    
    params = {
        "platform": platform,
        "review_listing_ids[]": token_number
    }
    
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        return response.json()  # Return the review data in JSON format
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def extract_text_after_question(paragraph):
    # Split the paragraph at the first occurrence of the question mark '?'
    parts = paragraph.split('?', 1)  # The '1' ensures splitting only at the first question mark
    
    # Check if there was a question mark and return the part after it
    if len(parts) > 1:
        return parts[1].strip()  # Strip to remove leading or trailing spaces
    else:
        return paragraph

def delete_listing(id):
    url = f'https://app.reviewflowz.com/api/v2/accounts/1900/listings/{id}'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer biebfR5mWeg36dVubbTUGEx5'
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print("Listing deleted successfully.")
    else:
        print(f"Failed to delete listing. Status code: {response.status_code}")

# Submit button    
# if st.button("Fetch Reviews"):
listing=get_listings(AUTH_TOKEN)
# st.write(listing)
if listing['pagination']['count']>=44:
    first_id=listing['data'][0]['id']
    delete_listing(first_id)
done=0
while True:
    listing=get_listings(AUTH_TOKEN)
    account_id=0
    have_id=0
    #to display all the listing 
    # st.write(listing)

    have_id,account_id=get_account_id(listing,have_id)
    if software_name and platform and site_url and have_id!=1:
        # st.write("I am running")
        profile_id, status_code = create_listing(software_name, platform, site_url)
        if status_code == 200 and profile_id:
            st.success(f"Listing created successfully for {software_name} on {platform}.")
            dashboard_url = f"https://app.reviewflowz.com/review_profiles/{profile_id}"
            st.write(f"Visit the dashboard: {dashboard_url}")
            new_listing=get_listings(AUTH_TOKEN)
            have_id,account_id=get_account_id(new_listing,have_id)

            st.write(f"Your id is {account_id}")
        # elif have_id!=1:
        #     st.error(f"Failed to create listing due to incorrect configurations . Status Code: {status_code}")
    elif have_id!=0:
        have_id=have_id
    else:
        st.error("Please fill out all fields.")
    new_listing=get_listings(AUTH_TOKEN)
    # st.write(new_listing)
    have_id,account_id=get_account_id(new_listing,have_id)
    # st.write(account_id)
    
    review_data = fetch_review(platform, account_id)
    if "error" in review_data:
        st.error(f"Failed to fetch the review: {review_data['error']}")
    elif review_data['data']!=[]:
        review=review_data
        sum1=0
        for i in range(len(review['data'])):
            sum1+=review['data'][i]['rating']
        overall_rating=sum1/len(review['data'])
        # st.write(review_data)
        st.markdown(f"**<span style='font-size: 28px;'>Overall Rating : {round(overall_rating,2)}</span>**",unsafe_allow_html=True)
        st.markdown("__________________________")
        for i in range(len(review['data'])):
            st.markdown(f"**<span style='font-size: 24px;'>{review['data'][i]['title']}</span>**",unsafe_allow_html=True)
            st.markdown(f"**<span style='font-size: 20px;'>Rating : {review['data'][i]['rating']}</span>**",unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: 18px;'>{extract_text_after_question(review['data'][i]['overall'])}</span>",unsafe_allow_html=True)
            st.markdown(f"**<span style='font-size: 18px;'>Pros :</span>** {review['data'][i]['pros']}",unsafe_allow_html=True)
            st.markdown(f"**<span style='font-size: 18px;'>Cons :</span>** {review['data'][i]['cons']}",unsafe_allow_html=True)
            st.markdown("__________________________")
        break


st.header("Some reviews fetched from Socials")
st.markdown("____________________________________________")

st.markdown(f"**<span style='font-size: 24px;'>message from luket (U0CMPKT0D) in macadmins.slack.com/#microsoft-intune</span>**",unsafe_allow_html=True)
st.markdown(f"**<span style='font-size: 18px;'>Posted on Slack</span>**",unsafe_allow_html=True)
st.markdown(f"<span style='font-size: 18px;'>Posted by : luket",unsafe_allow_html=True)
st.markdown('''That was our experience as well. We migrated from Jamf On-Prem to the Cloud, and it’s been smooth sailing ever since—the additional features have been great. Personally, I prefer to stick with Jamf Pro, and we’re currently exploring other products like Safe Internet and Protect.

We’re also evaluating whether we can reduce our Microsoft licensing costs, as we currently pay for A5. However, the decision to stay with Jamf or switch to Intune may ultimately be out of my hands.''')
st.markdown("[Open the post](https://macadmins.slack.com/?redir=%2Farchives%2FC31HJUSRJ%2Fp1726026827.382359%3Fthread_ts%3D1726008858.051969%26cid%3DC31HJUSRJ%26name%3DC31HJUSRJ%26perma%3D1726026827.382359)")

st.markdown("____________________________________________")

st.markdown(f"**<span style='font-size: 24px;'>message from mlbz521 (U492Y7FCH) in macadmins.slack.com/#jamf-product-issues</span>**",unsafe_allow_html=True)
st.markdown(f"**<span style='font-size: 18px;'>Posted on Slack</span>**",unsafe_allow_html=True)
st.markdown(f"**<span style='font-size: 18px;'>Posted by : mlbz521</span>**",unsafe_allow_html=True)
st.markdown(f"<span style='font-size: 18px;'>I just want to add, the migration to Jamf Cloud has been the most horrible experience I could have imagined. I didn't expect things to go smoothly, but....oh my gosh, the number of issues, completely screw ups, and simply the lack of care that they've shown to getting our environment working in a timely manner..... _*Wow*_</span>",unsafe_allow_html=True)
st.markdown("[Open the post](https://www.reddit.com/r/macsysadmin/comments/1eyk11f/comment/ljekstd/)",unsafe_allow_html=True)

st.markdown("____________________________________________")

st.markdown(f"**<span style='font-size: 24px;'>Recommendations Needed Moving From Jamf To A New</span>**",unsafe_allow_html=True)
st.markdown(f"**<span style='font-size: 18px;'>Posted on r/macsysadmin</span>**",unsafe_allow_html=True)
st.markdown(f"**<span style='font-size: 18px;'>Posted by : ITMule</span>**",unsafe_allow_html=True)
st.markdown(f"<span style='font-size: 18px;'>We migrated from Jamf to Mosyle (Fuse) years ago. Love it and price is amazing. If you end up deciding for Kandji, make sure to lock price for several years. Several people here at Reddit mentioned that first year price was good compared to Jamf, but every year at renewal they increase prices making it very similar to what was their Jamf price. We're with Mosyle for several years now and never had ANY price increase. They also never tried to increase prices. We just keep renewing at the same price with no issues. CFO loves it as it's one of the only tools we pay for that budget per employee is the same for several years.</span>",unsafe_allow_html=True)
st.markdown("[Open the post](https://macadmins.slack.com/?redir=%2Farchives%2FCAL8UHH1N%2Fp1727895669.874669%3Fthread_ts%3D1727895604.065859%26cid%3DCAL8UHH1N%26name%3DCAL8UHH1N%26perma%3D1727895669.874669)",unsafe_allow_html=True)

st.markdown("____________________________________________")

st.markdown(f"**<span style='font-size: 24px;'>Macos Password Issue</span>**",unsafe_allow_html=True)
st.markdown(f"**<span style='font-size: 18px;'>Posted on r/Intune</span>**",unsafe_allow_html=True)
st.markdown(f"**<span style='font-size: 18px;'>Posted by : disposeable1200</span>**",unsafe_allow_html=True)
st.markdown(f'''<span style='font-size: 18px;'>Nope. This is a flaw with Intune.

With Jamf you can store the password in extension attributes, but with Intune there's nowhere to store the password.

Maybe eventually Microsoft will implement this, but currently we're having to use Jamf alongside Intune.</span>''',unsafe_allow_html=True)
st.markdown("[Open the post](https://www.reddit.com/r/Intune/comments/1f7rt73/comment/llafcif/)",unsafe_allow_html=True)

st.markdown("____________________________________________")
