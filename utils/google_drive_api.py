import google
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class GoogleDriveApi:

    @classmethod
    def upload_audio_file_to_google_drive(cls, file_path):
        # Get default credentials
        creds, _ = google.auth.load_credentials_from_file("google-secret.json")

        # Create Drive API client
        service = build("drive", "v3", credentials=creds)

        # Extract file name and MIME type
        file_name = file_path.split("/")[-1]
        mime_type = "audio/wav" if file_path.endswith(".wav") else "audio/mpeg"

        # Prepare file metadata
        file_metadata = {"name": file_name}

        # Upload the file
        media = MediaFileUpload(file_path, mimetype=mime_type)
        uploaded_file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        file_id = uploaded_file.get("id")
        print(f"File ID: {file_id}")

        # Make the file publicly accessible
        service.permissions().create(
            fileId=file_id, body={"role": "reader", "type": "anyone"}
        ).execute()

        # Get the public URL
        public_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        print(f"File uploaded successfully: {public_url}")

        return public_url
