# create a streamlit app to let user give review to books stored in a bigquery table

import streamlit as st
import json
from google.cloud import bigquery
from google.cloud import storage
import os
# from dotenv import load_dotenv
from time import sleep
import time
import pandas as pd
from google.cloud import pubsub_v1
from datetime import datetime

# if local
# load environment variables
# load_dotenv()
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# create a client to access bigquery
client = bigquery.Client()

# get the table from bigquery
dataset_id = 'bookstore'
table_id = 'book-info-from-gcs'
table_ref = client.dataset(dataset_id).table(table_id)
table = client.get_table(table_ref)


query = """
    SELECT *
    FROM `bookstore`.`book-info-from-gcs`

"""
query_job = client.query(query)  # Make an API request.

book_dict = {}
dict_list_of_books = [{"title": "", "description": ""}]
project_id = "bookstore-398016"
topic_id = "books-review"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

for row in query_job:
    book_dict["title"] = row.title
    book_dict["image"] = row.image
    dict_list_of_books.append(book_dict.copy())

df = pd.DataFrame(dict_list_of_books)

def empty():
    ph.empty()
    sleep(0.05)

# Disable the submit button after it is clicked
def disable():
    st.session_state.disabled = True


# callback function when user select a book then display the description of the book
def book_selected():
    st.session_state.book_selected = True
    st.session_state.disabled = False


def review_published():
    st.session_state.review_published = True
    st.session_state.disabled = True


if 'book_selected' not in st.session_state:
    st.session_state.book_selected = None


if 'review_published' not in st.session_state:
    st.session_state.review_published = None

if 'disabled' not in st.session_state:
    st.session_state.disabled = False

if 'review_submitted' not in st.session_state:
    st.session_state.review_submitted = None

ph = st.empty()

col_1, col_2 = st.columns([2, 1])


with ph.container():
    empty()

    with col_1:

            # create a streamlit app to let user give review to books stored in a bigquery table
            st.title('Book Review App')

            # create a dropdown list to let user choose a book
            book_title = st.selectbox('Choose a book', df["title"], on_change=book_selected, disabled=st.session_state.disabled)

            # create a slider to let user give rating
            rating = st.slider('Rating', 0, 5, 0, disabled=st.session_state.disabled)

            # create a text input to let user give review
            review = st.text_input('Review', disabled=st.session_state.disabled)

            # create a button to let user submit the review
            review_submitted = st.button(label = 'Submit', on_click=disable, disabled=st.session_state.disabled)
        
            if review_submitted:
                submitted_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {"title": str(book_title), "star_rating": str(rating), "review": str(review), "review_timestamp": str(submitted_timestamp)}              
                data = json.dumps(data).encode("utf-8")
                publisher.publish(topic_path, data=data)
                review_published()
            if st.session_state.review_published:
                st.success("Your review for {} has been submitted!".format(book_title))

                
                    

    with col_2:
        if st.session_state.book_selected:
            empty()
            img = df[df["title"] == book_title]["image"].values[0]
            st.image(img)

