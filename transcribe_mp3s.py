#!/usr/bin/env python3
"""
Parallel MP3 Transcription Script using Gemini API
Works with Python 3.8+
"""

import os
import sys
import json
import base64
import time
import requests
from pathlib import Path
from typing import Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
API_KEY = "AIzaSyDbAJBhlPMB3frYnHFbKfXdD3XmEPqLrHw"  # Your API key
SOURCE_FOLDER = "input_mp3s"  # Folder containing MP3 files
OUTPUT_FOLDER = "output_transcripts"  # Folder for output transcripts
MAX_WORKERS = 4  # Number of parallel workers (adjust based on API rate limits)
DELAY_BETWEEN_REQUESTS = 1  # Seconds between requests per worker

# Gemini API endpoint
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}"

# Thread-safe printing
print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    """Thread-safe print function."""
    with print_lock:
        print(*args, **kwargs)

def create_folders():
    """Create necessary folders if they don't exist."""
    Path(SOURCE_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    safe_print(f"✓ Folders ready: {SOURCE_FOLDER} (input), {OUTPUT_FOLDER} (output)")

def get_mp3_files(folder: str) -> list:
    """Get all MP3 files from the specified folder."""
    mp3_files = []
    for file in Path(folder).glob("*.mp3"):
        mp3_files.append(file)
    return sorted(mp3_files)

def transcribe_audio_with_retry(file_path: Path, max_retries: int = 2) -> Optional[str]:
    """Transcribe an audio file using Gemini API with retry logic."""
    for attempt in range(max_retries + 1):
        try:
            safe_print(f"\nProcessing: {file_path.name} (attempt {attempt + 1})")
            
            # Read and encode the audio file
            safe_print(f"  Reading file: {file_path.name}")
            with open(file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Prepare the request
            headers = {
                'Content-Type': 'application/json',
            }
            
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": "Please transcribe this audio file completely and accurately. Provide only the transcription without any additional commentary:"
                        },
                        {
                            "inline_data": {
                                "mime_type": "audio/mp3",
                                "data": audio_base64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": 8192,
                }
            }
            
            # Make the API request with timeout
            safe_print(f"  Sending to Gemini API: {file_path.name}")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=300)
            
            if response.status_code == 429:  # Rate limit
                wait_time = (2 ** attempt) * 5  # Exponential backoff
                safe_print(f"  Rate limited, waiting {wait_time}s before retry: {file_path.name}")
                time.sleep(wait_time)
                continue
            elif response.status_code != 200:
                safe_print(f"  ✗ API Error for {file_path.name}: {response.status_code} - {response.text}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return None
            
            # Parse the response
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        transcription = parts[0]['text']
                        safe_print(f"  ✓ Transcription complete: {file_path.name}")
                        
                        
                        time.sleep(DELAY_BETWEEN_REQUESTS)
                        return transcription
            
            safe_print(f"  ✗ Unexpected response format: {file_path.name}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            return None
            
        except requests.exceptions.Timeout:
            safe_print(f"  ✗ Timeout error for {file_path.name}")
            if attempt < max_retries:
                safe_print(f"  Retrying {file_path.name} in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception as e:
            safe_print(f"  ✗ Error transcribing {file_path.name}: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            return None
    
    return None

def save_transcript(transcript: str, original_filename: str, output_folder: str) -> Path:
    """Save transcript to a text file."""
    output_filename = Path(original_filename).stem + "_transcript.txt"
    output_path = Path(output_folder) / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Transcript of: {original_filename}\n")
        f.write("=" * 50 + "\n\n")
        f.write(transcript)
    
    safe_print(f"  ✓ Saved transcript: {output_path}")
    return output_path

def process_single_file(file_info: Tuple[int, int, Path]) -> Tuple[bool, str]:
    """Process a single MP3 file. Returns (success, filename)."""
    index, total, mp3_file = file_info
    
    safe_print(f"\n[{index}/{total}] Starting: {mp3_file.name}")
    
    # Transcribe
    transcript = transcribe_audio_with_retry(mp3_file)
    
    if transcript:
        # Save transcript
        save_transcript(transcript, mp3_file.name, OUTPUT_FOLDER)
        return True, mp3_file.name
    else:
        safe_print(f"  ✗ Failed to transcribe: {mp3_file.name}")
        return False, mp3_file.name

def main():
    """Main execution function."""
    safe_print("=== Parallel Gemini MP3 Transcription Script ===\n")
    
    # Check API key
    if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        safe_print("ERROR: Please set your Gemini API key in the script!")
        safe_print("Get your key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    create_folders()
    
    # Get MP3 files
    mp3_files = get_mp3_files(SOURCE_FOLDER)
    
    if not mp3_files:
        safe_print(f"\nNo MP3 files found in {SOURCE_FOLDER}")
        safe_print("Please add MP3 files to the folder and run again.")
        sys.exit(0)
    
    safe_print(f"\nFound {len(mp3_files)} MP3 file(s) to process")
    safe_print(f"Using {MAX_WORKERS} parallel workers")
    
    # Check file sizes (Gemini has limits)
    large_files = []
    for mp3_file in mp3_files:
        file_size = mp3_file.stat().st_size / (1024 * 1024)  # Size in MB
        if file_size > 20:
            large_files.append((mp3_file.name, file_size))
            safe_print(f"⚠️  Warning: {mp3_file.name} is {file_size:.1f}MB. Large files may fail.")
    
    # Prepare file info tuples
    file_infos = [(i + 1, len(mp3_files), mp3_file) for i, mp3_file in enumerate(mp3_files)]
    
    # Process files in parallel
    successful = []
    failed = []
    start_time = time.time()
    
    safe_print(f"\nStarting parallel processing...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_single_file, file_info): file_info[2] 
            for file_info in file_infos
        }
        
        # Process completed tasks
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                success, filename = future.result()
                if success:
                    successful.append(filename)
                else:
                    failed.append(filename)
                
                # Progress update
                completed = len(successful) + len(failed)
                safe_print(f"\nProgress: {completed}/{len(mp3_files)} completed "
                          f"(✓ {len(successful)} successful, ✗ {len(failed)} failed)")
                
            except Exception as e:
                safe_print(f"  ✗ Unexpected error processing {file_path.name}: {e}")
                failed.append(file_path.name)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    safe_print("\n" + "=" * 60)
    safe_print(f"Processing complete!")
    safe_print(f"  Total time: {total_time:.1f} seconds")
    safe_print(f"  ✓ Successfully transcribed: {len(successful)}")
    if failed:
        safe_print(f"  ✗ Failed: {len(failed)}")
        safe_print(f"    Failed files: {', '.join(failed)}")
    safe_print(f"  Transcripts saved to: {OUTPUT_FOLDER}")
    
    if successful:
        avg_time = total_time / len(successful)
        safe_print(f"  Average time per successful file: {avg_time:.1f} seconds")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_print("\n\nScript interrupted by user.")
        sys.exit(0)
    except Exception as e:
        safe_print(f"\nUnexpected error: {e}")
        sys.exit(1)