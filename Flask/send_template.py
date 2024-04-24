import requests

def send_whatsapp_message(phone_number, template_name, language):
    # Define video links based on the chosen template
    video_link = ''
    if template_name == 'test_with_header':
        video_link = 'https://whatsapp.wbot.es/03.mp4'
    elif template_name == 'wbot_geo_with_video':
        video_link = 'https://whatsapp.wbot.es/02.mp4'

    # Your access token and from phone number ID
    access_token = ''
    from_phone_number_id = '106231419099043'

    # Prepare the message data
    message_data = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone_number,
        'type': 'template',
        'template': {
            'name': template_name,
            'language': {
                'code': language,
            },
            'components': [
                {
                    'type': 'header',
                    'parameters': [
                        {
                            'type': 'video',
                            'video': {
                                'link': video_link,
                            },
                        },
                    ],
                },
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'text': 'Giorgi Name',
                        },
                    ],
                },
                {
                    'type': 'BUTTON',
                    'index': '1',
                    'sub_type': 'url',
                },
            ],
        },
    }

    # Send the API request
    url = f'https://graph.facebook.com/v18.0/{from_phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = requests.post(url, json=message_data, headers=headers)

    if response.status_code == 200:
        return 'Message sent successfully'
    else:
        return f'Failed to send message. Status code: {response.status_code}\n{response.text}'

# Example of how to call the function:
phone_number = "34604107604"
template_name = "test_with_header"
language = "EN"

result = send_whatsapp_message(phone_number, template_name, language)
print(result)
