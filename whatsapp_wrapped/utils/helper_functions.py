import re
import pandas as pd
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

current_year = datetime.now().year
new_year = f"1/1/{str(current_year)}"
new_year_timestamp = pd.to_datetime(new_year, format="%m/%d/%Y").date()


def preprocess_chat(chat_data):
    """Convert chat into a list of lists consisting of date, time, sender, message."""
    chat_list = {}
    id = 0

    try:
        lines = chat_data.read().decode("utf-8").splitlines()

        for line in lines[1:]:
            if "<Media omitted>" not in line and not re.search(r"https?://\S+", line):
                try:
                    date_part, rest = line.split(" - ")
                    sender, message = rest.split(": ")
                    message = message.strip("\n")
                    msg_date, msg_time = date_part.split(", ")
                except ValueError:
                    pass
                chat_list[id] = [msg_date, msg_time, sender, message]
            id += 1
    except Exception as e:
        print(e)

    return chat_list


def make_df(data):
    df = pd.DataFrame.from_dict(
        data, orient="index", columns=["Date", "Time", "Sender", "Message"]
    )
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%y")

    df_subset = df[df["Date"].dt.date >= new_year_timestamp].copy()

    df_subset["Time"] = pd.to_datetime(df["Time"], format="%I:%M %p")
    df_subset["Time"] = df_subset["Time"].dt.time
    df_subset["Time Range"] = df_subset["Time"].apply(map_time_range)
    return df_subset


def map_time_range(timestamp):
    hour = timestamp.hour
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    elif 21 <= hour or hour < 3:
        return "night"
    else:
        return "dawn"


def analyze_sentiment(text):
    sentiment_scores = sia.polarity_scores(text)

    if sentiment_scores["compound"] >= 0.05:
        sentiment = "Positive"
    elif sentiment_scores["compound"] <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return sentiment

def get_top_initiator(df):
    first_records_per_date = df.groupby("Date").first()
    sc = first_records_per_date["Sender"].value_counts()
    return sc.to_dict()


def get_sentiment_percentages(df):
    message_list_by_sender_dict = df.groupby("Sender")["Message"].agg(list).to_dict()
    all_sentiments_in_percentage = {}

    for sender in message_list_by_sender_dict.keys():
        sender_messages = message_list_by_sender_dict[sender]
        sentiments = []

        for text in sender_messages:
            text_sentiment = analyze_sentiment(text)
            sentiments.append(text_sentiment)

        negatives = (sentiments.count("Negative") * 100) / len(sentiments)
        neutrals = (sentiments.count("Neutral") * 100) / len(sentiments)
        positives = (sentiments.count("Positive") * 100) / len(sentiments)

        sentiments_dict = {
            "positives": positives,
            "negatives": negatives,
            "neutrals": neutrals,
        }

        all_sentiments_in_percentage[sender] = sentiments_dict

    return all_sentiments_in_percentage

def get_message_count_stats(df):
    """Gets message counts of each participant in the chat

    Keyword arguments:
    df -- dataframe
    Return: dict containing chat participants and their mesage counts.
    """

    sender_value_counts = df.groupby("Sender")["Message"].count()
    return sender_value_counts.to_dict()