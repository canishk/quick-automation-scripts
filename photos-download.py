#Google Photos Download Script from the given URL
import requests
import os
import argparse
import json
import re

class GooglePhotosDownloader:
    def __init__(self, url, output_dir):
        self.url = url
        self.output_dir = output_dir

    def download_photos(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            photos = self.extract_photo_urls(response.text)
            self.save_photos(photos)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading photos: {e}")
    
    def extract_album_id(self):
        # Extract album ID from the URL
        patterns = [
            r'photos\.google\.com/share/([A-Za-z0-9_-]+)',
            r'photos\.app\.goo\.gl/([A-Za-z0-9]+)',
            r'key=([A-Za-z0-9_-]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, self.url)
            if match:
                return match.group(1)
        return None
    
    def fetch_album_content(self, album_id):
        """Fetch the album page and extract media items using regex + JSON parsing."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(f'https://photos.google.com/share/{album_id}', headers=headers)
        response.raise_for_status()
        return_html = response.text
        media_items = []
        json_matches = re.findall(r'(\[\s*\{[^}]*"url"[^}]*\}\s*\])', return_html, re.DOTALL)
        json_matches.extend(re.findall(r'(\{[^}]*"mediaItems"[^}]*\})', return_html, re.DOTALL))

        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'url' in item:
                            media_items.append(item)
                elif isinstance(data, dict) and 'mediaItems' in data:
                    media_items.extend(data['mediaItems'])
            except:
                continue
        # Fallback: extract direct image URLs (lh3.googleusercontent.com or similar)
        url_pattern = r'(https?://lh3\.googleusercontent\.com/[^"\']+?)(?=["\'])'
        urls = re.findall(url_pattern, return_html)
        for url in urls:
            #Clean and add the URLs
            clean_url = url.split('=')[0]  # Remove any parameters
            media_items.append({'url': clean_url})

        #Deduplicate media items based on URL
        unique_items = []
        

