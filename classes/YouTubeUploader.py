import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from alive_progress import alive_bar

class YouTubeUploader:
    def __init__(self, client_secrets_file='./config/client_secrets.json', credentials_file='./config/youtube_credentials.pickle'):
        self.client_secrets_file = client_secrets_file
        self.credentials_file = credentials_file
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.youtube = self.authenticate()

    def authenticate(self):
        credentials = None
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'rb') as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.scopes)
                credentials = flow.run_local_server(port=0)

            with open(self.credentials_file, 'wb') as token:
                pickle.dump(credentials, token)

        return build("youtube", "v3", credentials=credentials)

    def upload_video(self, file_path, title, description="", tags=None, privacy_status="private"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        media = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True, mimetype="video/*")

        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=request_body,
                media_body=media
            )
            
            return self._resumable_upload(request, file_path)
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def _resumable_upload(self, request, file_path):
        response = None
        total_size = os.path.getsize(file_path)
        uploaded_size = 0
        with alive_bar(100, manual=True, bar='filling', title="Upload video on yt") as bar: 
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status and status.resumable_progress:
                        uploaded_size = status.resumable_progress
                        percentage = int((uploaded_size / total_size) * 100)
                        bar.text(f"Upload progress: {percentage}%")
                        bar(percentage/100)
                    if response and 'id' in response:
                        print(f"Video uploaded successfully: https://www.youtube.com/watch?v={response['id']}")
                        return response
                except HttpError as e:
                    print(f"An error occurred: {e}")
                    return None
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    return None
            bar(1)

    def delete_video(self, video_id):
        try:
            response = self.youtube.videos().delete(id=video_id).execute()
            print(f"Video with ID {video_id} deleted successfully.")
            return response
        except HttpError as e:
            print(f"An error occurred: {e}")
            return None
