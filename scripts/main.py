import requests
from bs4 import BeautifulSoup
import json

from utils import *

nonce = extract_nonce()
total_pages, total_rows = get_sequoia_pagination_info()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.sequoiacap.com/our-companies/',
    'Content-Type': 'application/json',
    'Origin': 'https://www.sequoiacap.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=1',
}

gen_count = 0
for pg in range(1,total_pages+1):
  json_data = {
      'action': 'facetwp_refresh',
      'data': {
          'facets': {
              'categories': [],
              'partners': [],
              'stage_current': [],
              'stage_at_investment': [],
              'load-more': [],
          },
          'frozen_facets': {},
          'http_params': {
              'get': [],
              'uri': 'our-companies',
              'url_vars': [],
          },
          'template': 'wp',
          'extras': {
              'selections': True,
              'sort': 'default',
          },
          'soft_refresh': 1,
          'is_bfcache': 1,
          'first_load': 0,
          'paged': pg,
      },
  }

  response = requests.post('https://www.sequoiacap.com/our-companies/#all-panel',\
                           headers=headers, json=json_data)

  # Convert bytes to string
  response_str = response.content.decode('utf-8')

  # Parse JSON
  json_data = json.loads(response_str)

  # Extract HTML from JSON
  html_content = json_data['template']

  # Parse HTML with BeautifulSoup
  soup = BeautifulSoup(html_content, 'html.parser')

  comp_names = soup.find_all(class_="company-listing__cell-wide company-listing__head")
  comp_names = [text.get_text() for text in comp_names]

  partners_list = soup.find_all(class_="u-lg-hide company-listing__list")
  partners_list = [names for names in partners_list]

  # Extract the names from all li tags
  partners_list =[i.get_text(',') for i in partners_list]

  # Find the table an thed extract data
  table = soup.find('table')
  rows = table.find_all('tr')

  # Extract data from table rows
  data = []
  row_count = 0
  Loading = ''
  for i,row in enumerate(rows):
      cells = row.find_all('td')
      row_data = [cell.get_text().strip() for cell in cells]

      try:
        row_data_check = [cell.get_text().strip() for cell in cells][0]
      except IndexError as error:
        row_data_check = None
        continue
      if type(eval(row_data_check))==int:
        # print(row_count,comp_names[row_count], row_data[:-1])

        data_no = row_data[:-1][0]
        # ajax call for more company info
        companies_data = fetch_company_data(data_no,nonce)
        company_name = comp_names[row_count]
        short_description = row_data[:-1][1]
        current_stage = row_data[:-1][2]
        partners = partners_list[row_count]



        result ={'company_name':company_name,
                 'short_description':short_description,
                 'current_stage':current_stage,
                 'partners':partners}
        merged_dict = {**result, **companies_data}
        append_row_to_csv(file_path, row_dict=merged_dict, header=header_cols)

        row_count+=1
        gen_count+=1
  #       if gen_count==15:
  #         break
  # if pg==1:
  #   break
  print('page',pg)