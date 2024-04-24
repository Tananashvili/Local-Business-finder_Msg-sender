from bs4 import BeautifulSoup
import requests
import json
from flask import Flask, request, jsonify, render_template
import pandas as pd
import time
from datetime import datetime
from send_message import send_msg

app = Flask(__name__)

def send_message(msg, recipient):
    send_msg(recipient, msg)

    df = pd.read_excel('excels/received.xlsx', sheet_name='Sheet1')
    send_df = pd.read_excel('excels/sent.xlsx', sheet_name='Sheet1')
    filtered_df = df[df['number'] == int(recipient)]
    max_id = filtered_df['id'].max()
    timestamp = int(time.time())
    new_record = pd.DataFrame({'id': max_id + 1, 'name': 'Me', 'number': recipient, 'text': msg, 'timestamp': timestamp}, index=[len(df)])

    send_df = pd.concat([send_df, new_record])
    send_df.to_excel("excels/sent.xlsx", index=False)

@app.route('/')
def index():
    url = 'https://wapp.wbot.es/read_messages.php'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    soup_str = str(soup)
    parsed_data = json.loads(soup_str)

    prettified_data = []
    for i in parsed_data:
        i["payload"] = json.loads(i["payload"])
        prettified_data.append(i)

    members_to_response = []
    members_to_display = []
    for member in prettified_data:
        try:
            idi = member["id"]
            name = member['payload']['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
            number = member['payload']['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            message = member['payload']['entry'][0]['changes'][0]['value']['messages'][-1]
            type = message['type']

            if not type == 'text':
                attachment = message[type]['id']
                try:
                    text = message[type]['caption']
                except KeyError:
                    text = ''

            else:
                attachment = ''
                text = message['text']['body']
            
            member_to_response = {"id": idi, "name": name, "number": number, "text": text, 'attachment': attachment, 'timestamp': message['timestamp']}
            members_to_response.append(member_to_response)
            if number not in {member['number'] for member in members_to_display}:
                members_to_display.append(member_to_response)
        except KeyError:
            continue

    df = pd.DataFrame(members_to_response)
    df.to_excel("excels/received.xlsx", index=False)
    return render_template('index.html', members=members_to_display)

@app.route('/send_message', methods=['POST'])
def send_message_route():
    recipient = request.form['recipient']
    msg = request.form['message']

    # Call the send_message function with the recipient and message
    send_message(msg, recipient)

    return jsonify({"status": "success", "message": "Message sent successfully!"})

@app.route('/conversation/<int:number>')
def display_conversation(number):
    # Read received messages from "excels/received.xlsx"
    received_df = pd.read_excel("excels/received.xlsx")

    # Initialize an empty DataFrame for sent messages
    sent_df = pd.DataFrame()

    # Check if "excels/sent.xlsx" exists and is not empty
    try:
        sent_df = pd.read_excel("excels/sent.xlsx")
    except pd.errors.EmptyDataError:
        pass  # Handle the case where "excels/sent.xlsx" is empty

    # Filter received and sent messages based on the recipient's number
    received_messages = received_df[received_df['number'] == number]
    sent_messages = sent_df[sent_df['number'] == number]

    # Concatenate received and sent messages into one DataFrame
    conversation_data = pd.concat([received_messages, sent_messages])

    # Sort the conversation by 'timestamp' to display messages in chronological order
    conversation_data = conversation_data.sort_values(by='timestamp')

    # Convert the timestamp to a human-readable date format
    conversation_data['timestamp'] = conversation_data['timestamp'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))

    return render_template('conversation.html', conversation=conversation_data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
