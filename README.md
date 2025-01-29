# Text-to-Speech API with Bengali Support

This project provides a REST API for converting Bengali text to speech, generating WAV audio files with specific parameters, and creating configuration files for auto-dialer systems.

## Features

- Convert Bengali text to speech using Google Text-to-Speech (gTTS)
- Generate WAV audio files with specific parameters:
  - Mono channel
  - 8000Hz sample rate
  - 64kbps bitrate
- Create configuration files for auto-dialer systems
- API key authentication
- Detailed error logging

## Installation

### Prerequisites

1. Python 3.x
2. PHP 7.4 or higher
3. FFmpeg (required for audio conversion)

### System Dependencies

Install FFmpeg:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Python Dependencies

Install Python packages:
```bash
pip install -r requirements.txt
```

## Directory Structure

- `/var/www/html/test/audio_files/` - Directory for both WAV and TXT files
- `/var/www/html/test/text_to_speech.log` - Log file for debugging

## API Usage

### Endpoint

```
POST /api.php
```

### Headers

- `Content-Type: application/json`
- `X-API-Key: your_api_key`

### Request Body

```json
{
    "phone": "+8801712345678",
    "message": "আপনার বাংলা মেসেজ",
    "uuid": "123456789"
}
```

### Response

Success:
```json
{
    "status": "success",
    "message": "Message processed successfully",
    "data": {
        "phone": "+8801712345678",
        "message": "আপনার বাংলা মেসেজ",
        "audio_file": "123456789.wav",
        "timestamp": "2025-01-29 13:07:26"
    }
}
```

Error:
```json
{
    "status": "error",
    "message": "Error description",
    "data": null
}
```

## File Outputs

1. **WAV File**: 
   - Location: `/var/www/html/test/audio_files/{uuid}.wav`
   - Format: WAV (mono, 8000Hz, 64kbps)
   - Permissions: 644

2. **Configuration File**:
   - Location: `/var/www/html/test/audio_files/{uuid}.txt`
   - Format: Text file with auto-dialer configuration
   - Permissions: 644

## Error Handling

- Detailed error logging in `/var/www/html/test/text_to_speech.log`
- API returns appropriate error messages with HTTP status codes
- Input validation for phone numbers and required fields

## Security

- API key authentication required for all requests
- File permissions set to 644 for generated files
- Directory permissions set to 755

## Troubleshooting

1. Check the log file at `/var/www/html/test/text_to_speech.log`
2. Ensure FFmpeg is installed and accessible
3. Verify directory permissions for `/var/www/html/test/audio_files/`
4. Confirm Python dependencies are installed correctly

## License

This project is proprietary and confidential.
