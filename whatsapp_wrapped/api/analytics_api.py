from flask import Blueprint, request, jsonify
from whatsapp_wrapped.utils import *

analytics_api = Blueprint('analytics_api', __name__)


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

        if stats_type == 'message_count':
            stats = get_message_count_stats(df)
        elif stats_type == 'other_stat_type':
            stats = get_other_stat_type_stats(df)
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
    
    sender_value_counts = df['Sender'].value_counts()
    senders = sender_value_counts.index.tolist()
    message_counts = sender_value_counts.values.tolist()
    return dict(zip(senders, message_counts))


def get_other_stat_type_stats(df):
    return {'other_stat_type': 'Not implemented yet'}