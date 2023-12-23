import re
import pandas as pd
from datetime import datetime

current_year = datetime.now().year
new_year = pd.Timestamp('1/1/'+ str(current_year))

def preprocess_chat(chat_data):
    """Convert chat into a list of lists consisting of date, time, sender, message."""
    chat_list = {}
    id = 0

    try:
        lines = chat_data.read().decode('utf-8').splitlines()
    
        for line in lines[1:]:
            if '<Media omitted>' not in line and not re.search(r'https?://\S+', line):
                try:
                    date_part, rest = line.split(' - ')
                    sender, message = rest.split(': ')
                    message = message.strip('\n')
                    msg_date, msg_time = date_part.split(', ')
                except ValueError:
                    pass
                chat_list[id]= [msg_date, msg_time, sender, message]
            id +=1
    except Exception as e:
        print(e)
 
    return chat_list

def make_df(data):
    df = pd.DataFrame.from_dict(data, orient='index', columns=['Date', 'Time', 'Sender', 'Message'])
    df['Date'] =  pd.to_datetime(df['Date'])    
    df = df[df['Date']>= new_year]
    return df
