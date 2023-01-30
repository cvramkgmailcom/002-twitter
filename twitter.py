import streamlit as st
import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import timedelta, datetime
from pymongo import MongoClient
from bson.json_util import dumps, loads
import pymongo
import csv
import json


st.set_page_config(page_title="Twitter Search", page_icon="https://www.freepnglogos.com/uploads/twitter-logo-png/twitter-logo-vector-png-clipart-1.png", layout="wide")
# st.image('https://w7.pngwing.com/pngs/421/879/png-transparent-twitter-logo-social-media-iphone-organization-logo-twitter-computer-network-leaf-media.png', use_column_width=True, clamp=False)

# options = st.selectbox(
#     'What are your favorite colors',
#     ('Green', 'Yellow', 'Red', 'Blue'))

# csv = st.button("CSV", key=None, help=None, on_click=None, args=None, kwargs=None, type="secondary", disabled=False)



# st.write('You selected:', options)

# x = st.slider('x') 
# st.write(x, 'squared is', x * x)

# st.title("Making a button")
# result = st.button("Click Here")
# st.write(result)
# if result:
#     st.write(":smile:")

# if "visibility" not in st.session_state:
#     st.session_state.visibility = "visible"
#     st.session_state.disabled = False

st.markdown(""" <style> .font {
font-size:50px ; font-family: 'Cooper Black'; color: #1DA1F2;} 
</style> """, unsafe_allow_html=True)
st.markdown("""<img src=
"https://www.freepnglogos.com/uploads/twitter-logo-png/twitter-logo-vector-png-clipart-1.png"  width="50" height="50">
        <b>Twitter Data scrapper</b>
    </div>""", unsafe_allow_html=True)

text_input = st.text_input("Search Text box",placeholder="Provide your text here")


if text_input:
    st.write("You entered: ", text_input)


    t_data = pd.DataFrame(columns=['date', 'id','url', 'tweet_content', 'user','reply_count', 'retweet_count','language', 'source', 'like_count'])
    search_key_word = text_input

    since = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")

    search_input = str(search_key_word) + ' since:' +str(since)+ ' until:' + str(until)

    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(search_input).get_items()):
        if i>50:
            break
        t_data=t_data.append({'date':tweet.date,
        'id':tweet.id,
        'url':tweet.url,
        'tweet_content':tweet.content,
        'user':tweet.user.username,
        'reply_count':tweet.replyCount,
        'retweet_count':tweet.retweetCount,
        'language':tweet.lang,
        'source':tweet.source,
        'like_count':tweet.likeCount}, ignore_index=True)

    # Connect to MongoDB and create a new collection called 'tweets_give'
    client = MongoClient("mongodb://localhost:27017")
    print(client.list_database_names())
    db = client['Guvi']
    collection = db['collection']

    # Convert the pandas dataframe to a dictionary
    data_dict = t_data.to_dict('records')

    db.collection.delete_many({})
    db.collection.insert_many(data_dict)
    st.write("Hurah Your data is fetched the details are as follows")

    # collection = db['collection']
    # data=pd.DataFrame(list(collection.find()))
    # data.to_csv('data.csv',index=False)
    # st.write("Hi Your data is Exported")

    data=pd.DataFrame(list(collection.find()))
    # data = string = ftfy.fix_text(data)
    # if st.button("Download as CSV"):
    #     data.to_csv('dataN.csv',index=False)
    #     st.success("Data downloaded as CSV")
    # # if st.button("Download as JSON"):
    #     data.to_json('dataJ.json')
    #     st.success("Data downloaded as JSON")
    # json_data =data.to_json('dataJ.json')        
    # with open('dataNx.json', 'w') as file: 
    #     file.write(json_data)


    # data = {
    #     "Application_ID": ['BBC#:1010', 'NBA#:1111', 'BRC#:1212',
    #                     'SAC#:1412', 'QRD#:1912', 'BBA#:1092'],
    #     "MEETING_FILE_TYPE": [1, 2, 1, 4, 2, 4]
    # }


    # st.set_page_config(page_title='Matching Application Number', 
    #                 layout='wide')
    # # df = pd.read_csv('Analysis_1.csv')
    df = pd.DataFrame(data)

    st.sidebar.header("Filter Data:")
    sel_user = st.sidebar.multiselect(
        "Remove if you dont want any user data:",
        options=df['user'].unique(),
        default=df['user'].unique()
    )

    df_selection = df.query(
        'user == @sel_user'
    )
    num_records = len(df)

    # Display the number of records in a card
    st.markdown(f"# {num_records} records Fetched from twitter, the search term is {search_input}")
    st.dataframe(df_selection)

    # Show download button for the selected frame.
    # Ref.: https://docs.streamlit.io/library/api-reference/widgets/st.download_button
    csv = df_selection.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='selected_df.csv',
        mime='text/csv',
    )

    json = df_selection.to_json().encode('utf-8')
    st.download_button(
        label="Download data as JSON",
        data=json,
        file_name='selected_df.json',
        mime='text/json',
    )


    df_selection.to_excel('selected_df.xlsx', index=False)

    # Get the Excel file as bytes
    with open('selected_df.xlsx', 'rb') as f:
        excel_bytes = f.read()

    st.download_button(
            label="Download data as Excel",
            data=excel_bytes,
            file_name='selected_df.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
