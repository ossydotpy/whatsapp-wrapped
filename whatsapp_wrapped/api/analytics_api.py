from flask import Blueprint, request, jsonify
from whatsapp_wrapped.utils import analyze_sentiment, make_df, preprocess_chat

analytics_api = Blueprint('analytics_api', __name__)

time_ranges = {
    'morning': '6:00am - 11:59am',
    'afternoon': '12:00pm - 4:00pm',
    'evening': '4:01pm - 8:59pm',
    'night': '9:00pm - 3:00am',
    'dawn': '3:01am - 5:59am'
}

@analytics_api.route('/chat_stats', methods=['POST'])
def get_chat_stats():
    """
    Function to generate chat statistics.
    Return: returns requested chat statistics.
    """
    
    try:
        file = request.files.get('file')

        if not file:
            return jsonify({'error': 'No file part'}), 400

        cleaned_file_data = preprocess_chat(file)
        df = make_df(cleaned_file_data)

        stats_type = request.args.get('stats_type', 'message_count')

        if stats_type == 'individual_message_count':
            stats = get_message_count_stats(df)
        elif stats_type == 'message_count':
            stats = len(df)
        elif stats_type == 'peak_active_hours':
            timeofday = (lambda df: df['Time Range'].mode().tolist())(df)
            stats =  {
                'active_hours':timeofday[0],
                'time_range':time_ranges[timeofday[0]]
                }
        elif stats_type == 'top_initiator':
            stats = get_top_initiator(df)
        elif stats_type == 'sentiments':
            stats = get_sentiment_percentages(df)
        else:
            return jsonify({'error': f'Invalid stats_type: {stats_type}'}), 400

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def get_message_count_stats(df):
    """Gets message counts of each participant in the chat
    
    Keyword arguments:
    df -- dataframe
    Return: dict containing chat participants and their mesage counts.
    """
    
    sender_value_counts = df.groupby('Sender')['Message'].count()
    return sender_value_counts.to_dict()


def get_top_initiator(df):
    first_records_per_date = df.groupby('Date').first()
    sc = first_records_per_date['Sender'].value_counts()
    return sc.to_dict()

def get_sentiment_percentages(df):
    message_list_by_sender_dict = df.groupby('Sender')['Message'].agg(list).to_dict()
    all_sentiments_in_percentage = {}

    for sender in message_list_by_sender_dict.keys():
        sender_messages = message_list_by_sender_dict[sender]
        sentiments = []

        for text in sender_messages:
            text_sentiment = analyze_sentiment(text)
            sentiments.append(text_sentiment)

        negatives = (sentiments.count('Negative') * 100) / len(sentiments)
        neutrals = (sentiments.count('Neutral') * 100) / len(sentiments)
        positives = (sentiments.count('Positive') * 100) / len(sentiments)

        all_sentiments_in_percentage[sender] = [positives, negatives, neutrals]

    return all_sentiments_in_percentage
