import functions_framework
import json
from google.cloud import bigquery
from google.cloud import storage

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def hello_gcs(cloud_event):
    
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket_name = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket_name}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")

    client = bigquery.Client()
    dataset_id = 'bookstore'

    # get bucket
    bucket = storage.Client().get_bucket(bucket_name)
    # get blob
    blob = bucket.blob(name)
    # download blob as text
    text = blob.download_as_text(encoding='utf-8')
    json_data = json.loads(text)

    
    # insert data to gbq table
    if "scrape-cloudrun" in name:
        table_id = 'book-info-from-gcs'
        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)
        errors = client.insert_rows_json(table, json_data)
    elif "books-review" in name:
        table_id = 'books_review'
        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)
        errors = client.insert_rows_json(table, [json_data])
    
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))