import json
import os

import requests


class TranskriptorApi:
    @classmethod
    def transcribe_using_google_drive_url(google_drive_url):
        url = "https://api.tor.app/developer/transcription/url"

        # Replace with your actual API key
        api_key = os.getenv("TRANSKRIPTOR_TOKEN")

        # Set up the headers, including the API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        # Here, adjust the url, service, language, and optionally folder_id and file_name
        config = json.dumps(
            {
                "url": google_drive_url,
                "service": "Standard",
                "language": "en-US",
                "folder_id": "support",  # optional folder_id
                # "file_name": "example",  # optional file_name
            }
        )

        response = requests.post(url, headers=headers, data=config)
        response_json = response.json()

        # This is your order ID to check the status of the transcription
        return response_json["order_id"]

    @classmethod
    def transcribe_local_file(cls, file_path):
        # Step 1: Obtain the Upload URL
        url = "https://api.tor.app/developer/transcription/local_file/get_upload_url"

        # Replace with your actual API key
        api_key = os.getenv("TRANSKRIPTOR_TOKEN")

        # Set up the headers, including the API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        # Request body with the file name
        body = json.dumps({"file_name": "Sound file"})

        # Request to get the upload URL
        response = requests.post(url, headers=headers, data=body)
        if response.status_code != 200:
            raise Exception("Unable to get response of transkriptor url: ", response.status_code, response.text)
        response_json = response.json()
        upload_url = response_json["upload_url"]
        public_url = response_json["public_url"]

        # Step 2: Upload the Local File
        with open(file_path, "rb") as file_data:
            upload_response = requests.put(upload_url, data=file_data)
            if upload_response.status_code != 200:
                raise Exception("Unable to upload sound file")

        # Step 3: Initiate Transcription for the Uploaded File
        initiate_url = (
            "https://api.tor.app/developer/transcription/local_file/initiate_transcription"
        )

        # Configure transcription parameters
        config = json.dumps(
            {
                "url": public_url,  # Passing public_url to initiate transcription
                "language": "en-US",
                "service": "Standard",
                # "folder_id": "your_folder_id",  # Optional folder_id
                # "triggering_word": "example",  # Optional triggering_word
            }
        )

        # Send request to initiate transcription
        transcription_response = requests.post(initiate_url, headers=headers, data=config)
        if transcription_response.status_code != '202':
            raise Exception("Failed to transcribe file")

        transcription_json = transcription_response.json()
        return transcription_json['order_id']

    @classmethod
    def get_order_status(cls, order_id):
        api_key = os.getenv("TRANSKRIPTOR_TOKEN")

        # Set up the headers, including the API key
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }

        url = f"https://api.tor.app/developer/files/{order_id}/content"

        response = requests.get(url, headers=headers)
        response_json = response.json()
        if response.status_code in [400, 500, 404]:
            raise Exception(f"Error fetching order status: {response.status_code} - {response_json['message']}")

        if response_json['body']['status'] == 'Processing':
            raise Exception("Order is still processing")

        return response_json

    # Export format : Choose the export format: Txt, Srt, Pdf, or Docx
    @classmethod
    def register_webhook(cls, webhook_url, folder_id=None, export_format='Pdf'):
        import requests
        import json

        url = "https://api.tor.app/developer/integrations/webhooks/transcription_completed"
        api_key = os.getenv("TRANSKRIPTOR_TOKEN")

        # Set up the headers, including the API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        # Define the request body parameters
        # If you specify a folder_id, the webhook will only be triggered for transcriptions in that folder
        # If you do not specify a folder_id, the webhook will be triggered for the transcriptions in "Recent Files" folder
        body = {
            "url": webhook_url,
            "export_format": export_format,
            "include_timestamps": True,
            "include_speaker_names": True,
            "merge_same_speaker_segments": False,
            "is_single_paragraph": False,
            "paragraph_size": 1,
        }
        if folder_id:
            body["folder_id"] = folder_id

        # Send the POST request
        response = requests.post(url, headers=headers, data=json.dumps(body))

        return response.json()
