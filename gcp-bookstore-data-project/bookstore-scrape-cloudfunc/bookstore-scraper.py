import functions_framework
import requests
import lxml.html
import json
import os
from pprint import pprint
from google.cloud import storage
import time
from datetime import datetime
import unicodedata
import re

@functions_framework.http
def books_info_scrape(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'
    
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json-file
    storage_client = storage.Client()
    bucket_name = 'bookstore-scrape-project'

    bucket = storage_client.get_bucket(bucket_name)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    blob_name = f"scrape-cloudrun/booksinfo_{now}"
    blob = bucket.blob(blob_name)
    
    title_list = []
    start_time = time.time()
    for page in range(1, 50+1):
        URI = f'http://books.toscrape.com/catalogue/page-{page}.html'
        r = requests.get(URI)
        tree = lxml.html.fromstring(r.content)

        for i in range(1,21):
            title = tree.xpath(f'/html/body/div[1]/div/div/div/section/div[2]/ol/li[{i}]/article/h3/a')[0].get('title')
            title_list.append(title)
    
    item_list = []

    for i in range(0, 1000):

        try:
            book_title = [re.sub(" ", "-",re.sub('[^a-zA-Z0-9 -]', '', unicodedata.normalize('NFKD', title.lower()).encode('ASCII', 'ignore').decode('utf-8'))).replace("--", "-") for title in title_list]
            URI = f"""http://books.toscrape.com/catalogue/{book_title[i]}_{1000-i}/index.html"""
            
            r = requests.get(URI)
            tree = lxml.html.fromstring(r.content)
            book_dict = {}
            book_dict["title"] = tree.xpath('/html/body/div[1]/div/div[2]/div[2]/article/div[1]/div[2]/h1')[0].text_content()
            book_dict["image"] = tree.xpath('/html/body/div[1]/div/div[2]/div[2]/article/div[1]/div[1]/div/div/div/div/img')[0].get('src').replace('../../','http://books.toscrape.com/')
            book_dict["category"] = tree.xpath('/html/body/div[1]/div/ul/li[3]/a')[0].text_content()
            book_dict["price"] = tree.xpath('/html/body/div[1]/div/div[2]/div[2]/article/div[1]/div[2]/p[1]')[0].text_content()
            book_dict["instock_num"] = tree.xpath('/html/body/div[1]/div/div[2]/div[2]/article/div[1]/div[2]/p[2]')[0].text_content().strip().replace('In stock (','').replace(' available)','')
            book_dict["star_rating"] = tree.xpath('/html/body/div[1]/div/div[2]/div[2]/article/div[1]/div[2]/p[3]')[0].get('class').replace('star-rating ','')
            book_dict["description"] = tree.xpath('/html/body/div[1]/div/div[2]/div[2]/article/p')[0].text_content()
            item_list.append(book_dict)
        except:
            continue
    end_time = time.time()

    # item_list dump to json str
    item_list_json = json.dumps(item_list)
    upload = blob.upload_from_string(item_list_json)
    
    return f"{end_time - start_time} seconds", upload