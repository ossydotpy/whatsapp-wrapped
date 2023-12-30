from io import BytesIO
import os, re
import pandas as pd
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer
from PIL import Image, ImageDraw, ImageFont
from flask import url_for

sia = SentimentIntensityAnalyzer()

current_year = datetime.now().year
new_year = f"1/1/{str(current_year)}"
new_year_timestamp = pd.to_datetime(new_year, format="%m/%d/%Y").date()


def get_fonts_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, '..', 'static', 'fonts')
    return font_path

def get_img_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, '..', 'static', 'images')
    return font_path

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

def edit_count_image(some_api_result: dict):
    img_buffer = BytesIO()

    image = Image.open(f'{get_img_dir()}/message_count.png')
    width, height = image.size
    draw = ImageDraw.Draw(image)

    bold_font = ImageFont.truetype(f'{get_fonts_dir()}/OpenSans-Bold.ttf', 200)

    message_count = str(some_api_result.get('message_count', None))
    text_color = (255, 255, 255)
    position = (0.31 * width, 0.12 * height)

    draw.text(position, text=message_count, font=bold_font, fill=text_color)

    image.save(img_buffer, format='PNG')
    img_buffer.seek(0) 

    return img_buffer


def edit_top_initiator(some_api_result: dict):
    img_buffer = BytesIO()

    top_initiator = max(some_api_result['number_of_chat_initiations'],\
                         key=lambda k: some_api_result['number_of_chat_initiations'][k])
    value_counts = str(some_api_result['number_of_chat_initiations'][top_initiator])


    image = Image.open(f'{get_img_dir()}/initiator.png')
    width, height = image.size
    draw = ImageDraw.Draw(image)

    text_color = (0, 0, 0) 
    position1 = (0.20*width, 0.39*height)
    position2 = (0.13*width, 0.32*height)

    bold_font = ImageFont.truetype(f'{get_fonts_dir()}/OpenSans-Bold.ttf', 100)

    draw.text(position1, value_counts, font=bold_font, fill=text_color)
    draw.text(position2, top_initiator, font=bold_font, fill=text_color)

    image.save(img_buffer, format='PNG')
    img_buffer.seek(0) 

    return img_buffer


def edit_active_hours(some_api_result):
    text1 =some_api_result['peak_active_hours'].get('time_range', None)
    text2 = some_api_result['peak_active_hours'].get('peak_time', None)
    
    img_buffer = BytesIO()

    image = Image.open(f'{get_img_dir()}/active_hours.png')
    width, height = image.size
    draw = ImageDraw.Draw(image)

    text_color = (255, 255, 255) 
    position1 = (0.14*width, 0.48*height)
    position2 = (0.13*width, 0.32*height)

    bold_font = ImageFont.truetype(f'{get_fonts_dir()}/OpenSans-Bold.ttf', 100)

    draw.text(position1, text1, font=bold_font, fill=text_color)
    draw.text(position2, text2, font=bold_font, fill=text_color)

    image.save(img_buffer, format='PNG')
    img_buffer.seek(0) 

    return img_buffer

def edit_sentiment_analysis(some_api_result):
    img_buffer = BytesIO()

    image = Image.open(f'{get_img_dir()}/sentiment_analysis.png')
    width, height = image.size
    draw = ImageDraw.Draw(image)

    regular_font = ImageFont.truetype(f'{get_fonts_dir()}/OpenSans-Regular.ttf', 30)
    medium_font = ImageFont.truetype(f'{get_fonts_dir()}/OpenSans-Medium.ttf', 30)
    bottom_medium_font = ImageFont.truetype(f'{get_fonts_dir()}/OpenSans-Medium.ttf', 40)

    senders = list(some_api_result['sender_sentiment_percentage'].keys())

    sender_sentiment_percentage = some_api_result['sender_sentiment_percentage']

    most_positive_sender = None
    max_positive_percentage = -1

    for sender, sentiment_data in sender_sentiment_percentage.items():
        positive_percentage = sentiment_data['positives']
        
        if positive_percentage > max_positive_percentage:
            max_positive_percentage = positive_percentage
            most_positive_sender = sender

    format_sentiment = lambda sentiment: f"{round(sentiment, 2)} %"

    for idx, sender in enumerate(senders, start=1):
        sender_sentiment = some_api_result['sender_sentiment_percentage'].get(sender, {})

        cell_a = (0.10*width, (0.39 + (idx-1)*0.05)*height)
        cell_b = (0.40*width, (0.39 + (idx-1)*0.05)*height)
        cell_c = (0.60*width, (0.39 + (idx-1)*0.05)*height)
        cell_d = (0.80*width, (0.39 + (idx-1)*0.05)*height)

        draw.text(cell_a, sender, font=medium_font, fill=(255, 255, 255))
        draw.text(cell_b, format_sentiment(sender_sentiment.get('positives', 0)), font=regular_font, fill=(255, 255, 255))
        draw.text(cell_c, format_sentiment(sender_sentiment.get('negatives', 0)), font=regular_font, fill=(255, 255, 255))
        draw.text(cell_d, format_sentiment(sender_sentiment.get('neutrals', 0)), font=regular_font, fill=(255, 255, 255))

    most_positive_sender_position = (0.38*width, 0.535*height)
    draw.text(most_positive_sender_position, most_positive_sender, font=bottom_medium_font, fill=(255, 255, 255))

    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return img_buffer

def edit_individual_count_image(some_api_result: dict):
    img_buffer = BytesIO()

    image = Image.open(f'{get_img_dir()}/individual.png')
    text_color = (0, 0, 0)
    width, height = image.size
    draw = ImageDraw.Draw(image)

    bold_font = ImageFont.truetype(f'{get_fonts_dir()}/OpenSans-Bold.ttf', 150)

    counts = some_api_result.get('message_count_by_sender', None)
    senders = list(counts.keys())
    
    sender1 = senders[0]
    sender2 = senders[1]

    sender1_count = str(counts[sender1])
    sender2_count = str(counts[sender2])

    sender1_position = (0.02 * width, 0.58 * height)
    sender2_position = (0.59 * width, 0.68 * height)
    sender1_count_position = (0.05 * width, 0.67 * height)
    sender2_count_position = (0.61 * width, 0.78 * height)

    draw.text(sender1_position, text=sender1, font=bold_font, fill=text_color)
    draw.text(sender2_position, text=sender2, font=bold_font, fill=text_color)
    draw.text(sender1_count_position, text=sender1_count, font=bold_font, fill=text_color)
    draw.text(sender2_count_position, text=sender2_count, font=bold_font, fill=text_color)

    image.save(img_buffer, format='PNG')
    img_buffer.seek(0) 

    return img_buffer