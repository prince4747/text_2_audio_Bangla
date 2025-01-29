#!/usr/bin/env python3
import sys
import json
from gtts import gTTS
import os
from datetime import datetime
import logging
from pydub import AudioSegment
import tempfile
import traceback

# Set up logging
logging.basicConfig(
    filename='/var/www/html/test/text_to_speech.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define file paths
AUDIO_FILES_PATH = "/var/www/html/test/audio_files"
TXT_FILES_PATH = "/var/www/html/test/audio_files"  # Using same directory for both audio and txt files
#TXT_FILES_PATH = "/usr/src/file"  # Requires root permissions

def convert_to_wav_format(input_path, output_path):
    """Convert audio to WAV format with specific parameters"""
    try:
        logging.info(f"Starting audio conversion from {input_path} to {output_path}")
        
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Load the audio file
        audio = AudioSegment.from_mp3(input_path)
        logging.info("Successfully loaded MP3 file")
        
        # Convert to mono
        audio = audio.set_channels(1)
        logging.info("Converted to mono")
        
        # Set sample rate to 8000Hz
        audio = audio.set_frame_rate(8000)
        logging.info("Set sample rate to 8000Hz")
        
        # Export with specific parameters
        audio.export(
            output_path,
            format='wav',
            parameters=[
                "-ab", "64k",  # Set bitrate to 64k
                "-ar", "8000"  # Ensure sample rate is 8000Hz
            ]
        )
        
        # Verify the output file exists
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Failed to create output file: {output_path}")
            
        logging.info(f"Successfully converted audio to WAV format: {output_path}")
        return True
    except Exception as e:
        error_msg = f"Error converting audio format: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return False

def create_config_file(phone, uuid, script_dir):
    """Create config file with the required configuration using uuid as filename"""
    try:
        logging.info(f"Creating config file for phone: {phone}, uuid: {uuid}")
        
        # Create the config content
        config_content = [
            f"Channel:SIP/9610003003/{phone}",
            "CallerID:9610003003",
            "MaxRetries:0",
            "RetryTime:0",
            "WaitTime:30",
            "Context:autocall",
            f"Extension:{uuid}",
            "Priority:1",
            f"Set:foo={uuid}"
        ]
        
        logging.info(f"TXT files directory path: {TXT_FILES_PATH}")
        
        # Create config file in the txt directory with uuid as filename
        config_path = os.path.join(TXT_FILES_PATH, f"{uuid}.txt")
        
        # Ensure txt directory exists with proper permissions
        if not os.path.exists(TXT_FILES_PATH):
            os.makedirs(TXT_FILES_PATH, mode=0o755)
            logging.info(f"Created txt directory: {TXT_FILES_PATH}")
        
        # Write the config file with proper permissions
        with open(config_path, 'w') as f:
            f.write('\n'.join(config_content))
        os.chmod(config_path, 0o644)
        
        # Verify the file was created
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Failed to create config file: {config_path}")
            
        logging.info(f"Successfully created config file: {config_path}")
        return True, config_path
    except Exception as e:
        error_msg = f"Error creating config file: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return False, error_msg

def text_to_speech(text, phone, uuid):
    try:
        logging.info(f"Starting text-to-speech conversion for uuid: {uuid}, phone: {phone}")
        logging.info(f"Text to convert: {text[:50]}...")
        
        # Log current working directory
        current_dir = os.getcwd()
        logging.info(f"Current working directory: {current_dir}")
        
        # Create audio_files directory if it doesn't exist
        if not os.path.exists(AUDIO_FILES_PATH):
            os.makedirs(AUDIO_FILES_PATH, mode=0o755)
            logging.info(f"Created audio directory: {AUDIO_FILES_PATH}")
        
        # Create temporary MP3 file first
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
            temp_mp3_path = temp_mp3.name
            logging.info(f"Created temporary MP3 file: {temp_mp3_path}")
        
        try:
            # Convert text to speech (MP3 format first)
            logging.info("Converting text to speech with gTTS...")
            tts = gTTS(text=text, lang='bn')  # 'bn' is the language code for Bangla
            tts.save(temp_mp3_path)
            logging.info("Successfully saved MP3 file")
            
            # Create final WAV filename
            filename = f"{uuid}.wav"
            filepath = os.path.join(AUDIO_FILES_PATH, filename)
            logging.info(f"Target WAV file path: {filepath}")
            
            # Convert to WAV with specific parameters
            if not convert_to_wav_format(temp_mp3_path, filepath):
                raise Exception("Failed to convert audio to WAV format")
                
            # Set permissions for WAV file
            os.chmod(filepath, 0o644)
            logging.info("Set file permissions")
            
            # Create config file
            config_created, config_result = create_config_file(phone, uuid, None)
            if not config_created:
                raise Exception(f"Failed to create config file: {config_result}")
            
            # Return success response
            response = {
                "status": "success",
                "audio_file": filename,
                "config_file": f"{uuid}.txt",
                "audio_path": filepath,
                "config_path": config_result
            }
            
        finally:
            # Clean up temporary MP3 file
            if os.path.exists(temp_mp3_path):
                os.unlink(temp_mp3_path)
                logging.info("Cleaned up temporary MP3 file")
        
    except Exception as e:
        error_msg = f"Error in text_to_speech: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        response = {
            "status": "error",
            "message": error_msg
        }
    
    # Print JSON response for PHP to capture
    print(json.dumps(response))

if __name__ == "__main__":
    try:
        logging.info("Script started")
        logging.info(f"Python version: {sys.version}")
        logging.info(f"Arguments received: {sys.argv}")
        
        # Read input JSON from command line argument
        if len(sys.argv) > 1:
            try:
                input_json = sys.argv[1]
                logging.debug(f"Received input: {input_json}")
                
                input_data = json.loads(input_json)
                if not isinstance(input_data, dict):
                    raise ValueError("Input must be a JSON object")
                
                if not all(key in input_data for key in ['message', 'phone', 'uuid']):
                    raise ValueError("Input must contain 'message', 'phone', and 'uuid' fields")
                
                text_to_speech(input_data['message'], input_data['phone'], input_data['uuid'])
                
            except json.JSONDecodeError as e:
                error_msg = f"JSON decode error: {str(e)}"
                logging.error(error_msg)
                print(json.dumps({
                    "status": "error",
                    "message": error_msg
                }))
            except Exception as e:
                error_msg = f"Error processing input: {str(e)}\n{traceback.format_exc()}"
                logging.error(error_msg)
                print(json.dumps({
                    "status": "error",
                    "message": error_msg
                }))
        else:
            error_msg = "No input provided"
            logging.error(error_msg)
            print(json.dumps({
                "status": "error",
                "message": error_msg
            }))
    except Exception as e:
        error_msg = f"Fatal error: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        print(json.dumps({
            "status": "error",
            "message": error_msg
        }))
