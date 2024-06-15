import requests
from bs4 import BeautifulSoup
import json
import csv
import re

# Function to append a single row to CSV
def append_row_to_csv(file_path, row_dict, header=None):

    file_exists = False
    try:
        with open(file_path, 'r') as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)

# File path
file_path = 'data.csv'

header_cols = ['company_name','short_description','current_stage','partners',\
          'full_description','logo_link','website_link','twitter_link',\
          'linkedin_link','instagram_link','youtube_link','job_titles',\
          'team_members','founded_year','partnered_year','ipo_year','acquired_year',\
               'categories','job_link']



def extract_nonce():
  """
  Extracts the nonce value from the given BeautifulSoup object.

  Args:
    soup: A BeautifulSoup object representing the HTML document.

  Returns:
    The nonce value as a string, or None if not found.
  """
  response = requests.get('https://www.sequoiacap.com/our-companies/#all-panel')
  soup = BeautifulSoup(response.content, 'html.parser')
  script_tag = soup.find('script', {'id': 'theme-scripts-js-before'})
  if script_tag and script_tag.string:
    nonce_match = re.search(r'"nonce":"(.*?)"', script_tag.string)
    if nonce_match:
      return nonce_match.group(1)
  return None



def fetch_company_data(post_id:str,nonce:str):

    """
    Fetch and parse company data from the Sequoia Capital website.

    This function sends a POST request to the Sequoia Capital website to retrieve
    company-related information based on a provided post ID and nonce. It parses the
    HTML response to extract various details about the company, such as description,
    social media links, milestones, team members, and job titles.

    Args:
        post_id (str): The ID of the post to fetch company data for.
        nonce (str): A nonce value for authentication.

    Returns:
        dict: A dictionary containing the extracted company information:
            - 'full_description' (str or None): The full description of the company.
            - 'logo_link' (str or None): URL of the company logo.
            - 'website_link' (str or None): URL of the company's website.
            - 'twitter_link' (str or None): URL of the company's Twitter profile.
            - 'linkedin_link' (str or None): URL of the company's LinkedIn profile.
            - 'instagram_link' (str or None): URL of the company's Instagram profile.
            - 'youtube_link' (str or None): URL of the company's YouTube channel.
            - 'job_titles' (list of str or None): A list of job titles associated with the company.
            - 'team_members' (list of str or None): A list of team members in the company.
            - 'founded_year' (str or None): The year the company was founded.
            - 'partnered_year' (str or None): The year the company partnered with Sequoia.
            - 'ipo_year' (str or None): The year the company went public.
            - 'acquired_year' (str or None): The year the company was acquired.
            - 'categories' (list of str or None): A list of categories the company belongs to.
            - 'job_link' (str or None): URL of the company's job listings page.

    Raises:
        requests.RequestException: If the POST request fails.
        Exception: If there is a general failure in data extraction.

    Example:
        >>> fetch_company_data('12345', 'abcde12345')
        {
            'full_description': 'This is a detailed description of the company...',
            'logo_link': 'https://example.com/logo.png',
            'website_link': 'https://example.com',
            'twitter_link': 'https://twitter.com/example',
            'linkedin_link': 'https://linkedin.com/company/example',
            'instagram_link': 'https://instagram.com/example',
            'youtube_link': 'https://youtube.com/channel/example',
            'job_titles': ['Software Engineer', 'Data Scientist'],
            'team_members': ['John Doe', 'Jane Smith'],
            'founded_year': '2000',
            'partnered_year': '2005',
            'ipo_year': '2010',
            'acquired_year': '2018',
            'categories': ['Technology', 'Finance'],
            'job_link': 'https://example.com/jobs'
        }
    """

    url = 'https://www.sequoiacap.com/wp-admin/admin-ajax.php'
    data = {
        'action': 'load_company_content',
        'post_id': post_id,
        'nonce': nonce,
    }

    # Sending the POST request
    response = requests.post(url, headers= None, data=data)

    # Clean the response text
    cleaned_text = re.sub(r'\s*\t+\s*', ' ', response.text)
    cleaned_text = cleaned_text.encode('utf-8').decode('ascii', errors='ignore')

    # Parse the cleaned text with BeautifulSoup
    text_soup = BeautifulSoup(cleaned_text, 'html.parser')

    # Extracting information with error handling
    try:
        full_description = text_soup.find(class_='wysiwyg').get_text(strip=True)
    except AttributeError:
        full_description = None
    try:
        logo_link = text_soup.select_one('img')['src']
    except (AttributeError, TypeError):
        logo_link = None

    try:
        website_link = text_soup.select_one('a')['href']
    except (AttributeError, TypeError):
        website_link = None

    try:
        twitter_link = text_soup.find(class_='ico--twitter')['href']
    except (AttributeError, TypeError):
        twitter_link = None

    try:
        linkedin_link = text_soup.find(class_='ico--linkedin')['href']
    except (AttributeError, TypeError):
        linkedin_link = None

    try:
        instagram_link = text_soup.find(class_='ico--instagram')['href']
    except (AttributeError, TypeError):
        instagram_link = None

    try:
        youtube_link = text_soup.find(class_='ico--youtube')['href']
    except (AttributeError, TypeError):
        youtube_link = None

    try:
        job_titles = [job.get_text(strip=True) for job in text_soup.select('.clist__title:-soup-contains("Jobs") ~ ul.clist__list .clist__link')]
    except AttributeError:
        job_titles = None

    try:
        team_members = [member.get_text(strip=True) for member in text_soup.select('.clist__title:-soup-contains("Team") ~ ul.clist__list .clist__link')]
    except AttributeError:
        team_members = None

    try:
        founded_year = text_soup.select_one('.clist__title:-soup-contains("Milestones") ~ ul.clist__list .clist__item:-soup-contains("Founded")').get_text(strip=True).split()[-1]
    except (AttributeError, TypeError, IndexError):
        founded_year = None

    try:
        partnered_year = text_soup.select_one('.clist__title:-soup-contains("Milestones") ~ ul.clist__list .clist__item:-soup-contains("Partnered")').get_text(strip=True).split()[-1]
    except (AttributeError, TypeError, IndexError):
        partnered_year = None

    try:
        ipo_year = text_soup.select_one('.clist__title:-soup-contains("Milestones") ~ ul.clist__list .clist__item:-soup-contains("IPO")').get_text(strip=True).split()[-1]
    except (AttributeError, TypeError, IndexError):
        ipo_year = None

    try:
        acquired_year = text_soup.select_one('.clist__title:-soup-contains("Milestones") ~ ul.clist__list .clist__item:-soup-contains("Acquired")').get_text(strip=True).split()[-1]
    except (AttributeError, TypeError, IndexError):
        acquired_year = None

    try:
        categories = [category.get_text(strip=True) for category in text_soup.select('.l-hr-row__item a.pill')]
    except AttributeError:
        categories = None

    try:
        job_link = text_soup.select_one('.caption.caption--14')['href']
    except (AttributeError, TypeError):
        job_link = None



    # Returning the extracted information
    return {
        'full_description': full_description,
        'logo_link': logo_link,
        'website_link': website_link,
        'twitter_link': twitter_link,
        'linkedin_link': linkedin_link,
        'instagram_link': instagram_link,
        'youtube_link': youtube_link,
        'job_titles': job_titles,
        'team_members': team_members,
        'founded_year': founded_year,
        'partnered_year': partnered_year,
        'ipo_year': ipo_year,
        'acquired_year': acquired_year,
        'categories': categories,
        'job_link': job_link,
    }



def get_sequoia_pagination_info():
    """
    Retrieve pagination information from the Sequoia Capital website.

    This function fetches and parses the necessary page or API endpoint to determine
    the total number of pages and the total number of rows available in the data.

    Returns:
        tuple: A tuple containing:
            - total_pages (int): The total number of pages.
            - total_rows (int): The total number of rows.

    Raises:
        requests.RequestException: If the request to the page or API fails.
        ValueError: If the pagination information cannot be found or parsed.

    Example:
        >>> total_pages, total_rows = get_sequoia_pagination_info()
        >>> print(f"Total pages: {total_pages}, Total rows: {total_rows}")
        Total pages: 10, Total rows: 150
    """
    # Fetch the HTML content
    response = requests.get('https://www.sequoiacap.com/our-companies/#all-panel')

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the <script> tag containing the desired JavaScript object
    page_script_tag = soup.find('script', string=re.compile('window.FWP_JSON'))

    if not page_script_tag:
        raise Exception("Unable to find the script tag containing 'window.FWP_JSON'")

    # Extract the JavaScript object as a string
    js_code = page_script_tag.string

    # Use regex to isolate the JSON part
    json_match = re.search(r'window\.FWP_JSON\s*=\s*(\{.*\});', js_code)

    if not json_match:
        raise Exception("Unable to extract JSON from the script tag")

    json_str = json_match.group(1)

    # Parse the JSON
    data = json.loads(json_str)

    # Extract pagination information
    total_pages = data['preload_data']['settings']['pager']['total_pages']
    total_rows = data['preload_data']['settings']['pager']['total_rows']

    return total_pages, total_rows
