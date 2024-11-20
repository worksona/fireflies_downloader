import os
import requests
from datetime import datetime
import json

class FirefliesDownloader:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.fireflies.ai/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def fetch_meetings(self, start_date=None, end_date=None):
        query = """
        query GetTranscripts($fromDate: DateTime, $toDate: DateTime, $limit: Int) {
            transcripts(fromDate: $fromDate, toDate: $toDate, limit: $limit) {
                id
                title
                date
                duration
                transcript_url
                audio_url
                summary {
                    keywords
                    action_items
                }
            }
        }
        """
        
        # Convert dates to ISO format for DateTime
        if start_date:
            start_date = f"{start_date}T00:00:00Z"
        if end_date:
            end_date = f"{end_date}T23:59:59Z"
            
        variables = {
            "limit": 50,
            "fromDate": start_date,
            "toDate": end_date
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables}
            )
            
            if response.status_code == 400:
                error_detail = response.json()
                print(f"API Error Details:")
                print(f"Status Code: {response.status_code}")
                print(f"Response Body: {json.dumps(error_detail, indent=2)}")
                return []
                
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                print(f"GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
                return []
            
            print(f"API Response: {json.dumps(data, indent=2)}")
            return data.get("data", {}).get("transcripts", [])
            
        except requests.exceptions.RequestException as e:
            print(f"Network Error: {str(e)}")
            return []
        except json.JSONDecodeError:
            print(f"Invalid JSON response: {response.text}")
            return []
        except KeyError as e:
            print(f"Unexpected response structure: {str(e)}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return []

    def get_transcript(self, transcript_id):
        """Fetch a specific transcript by ID"""
        query = """
        query Transcript($transcriptId: String!) {
            transcript(id: $transcriptId) {
                id
                title
                date
                duration
                transcript_url
                audio_url
                sentences {
                    text
                    speaker_id
                    start_time
                }
                summary {
                    keywords
                    action_items
                }
            }
        }
        """
        
        variables = {
            "transcriptId": transcript_id
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables}
            )
            
            if response.status_code == 400:
                error_detail = response.json()
                print(f"API Error Details:")
                print(f"Status Code: {response.status_code}")
                print(f"Response Body: {json.dumps(error_detail, indent=2)}")
                return None
                
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                print(f"GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
                return None
            
            return data.get("data", {}).get("transcript")
            
        except requests.exceptions.RequestException as e:
            print(f"Network Error: {str(e)}")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON response: {response.text}")
            return None
        except KeyError as e:
            print(f"Unexpected response structure: {str(e)}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return None

    def download_file(self, url, filename):
        """Generic file download function"""
        if not url:
            print(f"No URL provided for {filename}")
            return None
            
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {str(e)}")
            print(f"URL: {url}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def save_file(self, content, filename):
        """Save content to file, creating directories if needed"""
        if content:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(content)
            print(f"Saved: {filename}")
        else:
            print(f"No content to save for: {filename}")

    def download_all(self, output_dir="fireflies_downloads", start_date=None, end_date=None):
        """Download all meetings within the specified date range"""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Format dates if provided
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                print("Invalid start date format. Use YYYY-MM-DD")
                return
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                print("Invalid end date format. Use YYYY-MM-DD")
                return

        # Fetch all meetings
        meetings = self.fetch_meetings(start_date, end_date)
        
        if not meetings:
            print("No meetings found or error occurred while fetching meetings.")
            return

        for meeting in meetings:
            # Create meeting-specific directory
            meeting_date = datetime.fromtimestamp(int(meeting["date"])/1000).strftime('%Y-%m-%d')
            meeting_title = meeting["title"].replace("/", "-").replace("\\", "-")
            meeting_dir = os.path.join(output_dir, f"{meeting_date}_{meeting_title}")
            
            # Get full transcript data
            transcript_data = self.get_transcript(meeting["id"])
            if transcript_data:
                # Save transcript data
                self.save_file(
                    json.dumps(transcript_data, indent=2).encode('utf-8'),
                    os.path.join(meeting_dir, "transcript.json")
                )
            
            # Download and save audio
            audio = self.download_file(meeting.get("audio_url"), "audio")
            if audio:
                self.save_file(audio, os.path.join(meeting_dir, "recording.mp3"))

            # Save meeting metadata
            metadata = {
                "id": meeting["id"],
                "title": meeting["title"],
                "date": meeting["date"],
                "duration": meeting["duration"],
                "transcript_url": meeting.get("transcript_url"),
                "audio_url": meeting.get("audio_url"),
                "summary": meeting.get("summary", {})
            }
            self.save_file(
                json.dumps(metadata, indent=2).encode('utf-8'),
                os.path.join(meeting_dir, "metadata.json")
            )

def main():
    print("Fireflies.ai Meeting Downloader")
    print("------------------------------")
    
    # Get API key from environment variable or user input
    api_key = os.getenv("FIREFLIES_API_KEY")
    if not api_key:
        api_key = input("Enter your Fireflies.ai API key: ")
    
    if not api_key.strip():
        print("Error: API key is required")
        return

    # Initialize downloader
    downloader = FirefliesDownloader(api_key)

    # Ask if user wants to download a specific transcript or all meetings
    choice = input("Enter '1' to download a specific transcript, or '2' to download all meetings: ")
    
    if choice == '1':
        transcript_id = input("Enter the transcript ID: ")
        if transcript_id:
            transcript_data = downloader.get_transcript(transcript_id)
            if transcript_data:
                output_dir = "fireflies_downloads"
                os.makedirs(output_dir, exist_ok=True)
                meeting_title = transcript_data["title"].replace("/", "-").replace("\\", "-")
                meeting_date = datetime.fromtimestamp(int(transcript_data["date"])/1000).strftime('%Y-%m-%d')
                meeting_dir = os.path.join(output_dir, f"{meeting_date}_{meeting_title}")
                
                # Save transcript data
                downloader.save_file(
                    json.dumps(transcript_data, indent=2).encode('utf-8'),
                    os.path.join(meeting_dir, "transcript.json")
                )
                print(f"Transcript saved to {meeting_dir}")
    else:
        # Optional date range
        start_date = input("Enter start date (YYYY-MM-DD) or press Enter to skip: ")
        end_date = input("Enter end date (YYYY-MM-DD) or press Enter to skip: ")

        # Download all files
        print("\nStarting download process...")
        downloader.download_all(
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None
        )

if __name__ == "__main__":
    main()
