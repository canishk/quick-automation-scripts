import gdown
import os
import time
import argparse
from requests.exceptions import ChunkedEncodingError, ConnectionError

def download_drive_contents(url, output_dir):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    if 'folders' in url or 'drive/folders' in url:
        # It's a folder URL
        gdown.download_folder(
            url=url,
            output=output_dir,
            quiet=False,
            remaining_ok=True,
            resume=True
        )
    else:
        # It's a file URL
        gdown.download(
            url=url,
            output=output_dir,
            quiet=False,
            fuzzy=True
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files or folders from Google Drive.")
    parser.add_argument("url", help="The Google Drive URL (file or folder)")
    parser.add_argument("output_dir", help="The output directory to save the downloaded content")
    parser.add_argument("--max-retries", type=int, default=10, help="Maximum number of retries on failure (default: 10)")
    
    args = parser.parse_args()
    
    max_retries = args.max_retries
    for attempt in range(max_retries):
        try:
            download_drive_contents(args.url, args.output_dir)
            print("Download completed successfully.")
            break
        
        except (ChunkedEncodingError, ConnectionError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 60  # 1 minute
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Download failed.")
                raise