# FirefliesDownloader

A Python script for downloading transcripts, audio recordings, and metadata from Fireflies.ai meetings.

## Features

- Download transcripts from specific meetings using transcript IDs
- Batch download all meetings within a specified date range
- Downloads include:
  - Full transcript data (JSON)
  - Audio recordings (MP3)
  - Meeting metadata (JSON)
- Automatic organization of downloaded files by date and meeting title
- Support for both environment variable and manual API key input
- Comprehensive error handling and logging

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- Fireflies.ai API key

## Installation

1. Clone or download this repository
2. Install required dependencies:
```bash
pip install requests
```

## Usage

### Running the Script

```bash
python fireflies_downloader.py
```

### Configuration

You can provide your Fireflies.ai API key in two ways:
1. Set it as an environment variable:
```bash
export FIREFLIES_API_KEY=your_api_key_here
```
2. Enter it when prompted by the script

### Options

The script provides two main options:

1. Download a specific transcript:
   - Choose option 1 when prompted
   - Enter the transcript ID
   - Files will be saved in a directory named after the meeting date and title

2. Download all meetings:
   - Choose option 2 when prompted
   - Optionally specify a date range (YYYY-MM-DD format)
   - All meetings within the range will be downloaded and organized by date

### Output Structure

Downloads are organized in the following structure:
```
fireflies_downloads/
└── YYYY-MM-DD_Meeting_Title/
    ├── transcript.json    # Full transcript data
    ├── recording.mp3     # Audio recording
    └── metadata.json     # Meeting metadata
```

## API Response Format

The script handles the following data from the Fireflies.ai API:

- Meeting metadata:
  - ID
  - Title
  - Date
  - Duration
  - Transcript URL
  - Audio URL

- Transcript data:
  - Text content
  - Speaker information
  - Timestamps
  - Summary
  - Keywords
  - Action items

## Error Handling

The script includes comprehensive error handling for:
- Network errors
- Invalid API responses
- Authentication issues
- Invalid date formats
- File system operations

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
