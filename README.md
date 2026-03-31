# Google Drive Downloader

A Python script to download files or folders from Google Drive using the `gdown` library. It supports automatic retries on network errors and can handle both individual files and entire folders.

## Features

- Download single files or entire folders from Google Drive
- Automatic retry mechanism for network failures
- Resume interrupted downloads
- Command-line interface with options

## Requirements

- Python 3.6 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script from the command line with the following syntax:

```bash
python gdrive-download.py <URL> <OUTPUT_DIR> [OPTIONS]
```

### Arguments

- `URL`: The Google Drive URL of the file or folder to download. For folders, use the shared folder URL.
- `OUTPUT_DIR`: The local directory where the downloaded content will be saved.

### Options

- `--max-retries N`: Maximum number of retries on failure (default: 10). If a download fails due to network issues, the script will wait 60 seconds and retry up to this many times.

### Examples

Download a single file:

```bash
python gdrive-download.py "https://drive.google.com/file/d/1ABC123.../view?usp=sharing" ./downloads
```

Download a folder:

```bash
python gdrive-download.py "https://drive.google.com/drive/folders/1DEF456.../?usp=sharing" ./downloads
```

Download with custom retry count:

```bash
python gdrive-download.py "https://drive.google.com/file/d/1ABC123.../view?usp=sharing" ./downloads --max-retries 5
```

## Notes

- For folder downloads, ensure the folder is publicly shared or you have access to it.
- The script creates the output directory if it doesn't exist.
- Downloads are resumed automatically if interrupted.
