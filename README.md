# S3 Bucket folder downloader
Python script to download the contents of S3 Bucket folders and zip it.

## Setup

1. Set PowerShell execution policy to allow scripts:
   ```
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. Activate the Python virtual environment:
   ```
   .\.venv\Scripts\Activate.ps1
   ```

3. Install AWS CLI and configure it as needed for accessing the account.

## Usage - S3 Downloader

1. Install Python dependencies in `.venv`:
   ```powershell
   python -m pip install -r s3-downloader_requirements.txt
   ```

2. Run the s3-downloader script:
   ```powershell
   python .\s3-downloader.py --bucket <BUCKET_NAME> [--folder <MAIN_FOLDER>] [--delete-source] [--destination <DESTINATION_PATH>]
   ```

### Arguments

- `--bucket` (required): S3 bucket name, e.g. `anish-photo-backup`
- `--folder` (optional): top-level folder in the bucket to process (e.g. `anish-phone` or `anish-phone/`).
- `--delete-source` (optional): delete the downloaded objects from S3 after successful zip archive creation.
- `--destination` (optional): destination directory for temporary and zip files (default: current working directory).

### Behavior

- Without `--folder`, downloads each top-level folder from the bucket and creates `.zip` files under a local folder named after the bucket.
- With `--folder`, downloads contents only under the specified folder prefix, zips subfolders inside that folder.
- If `--delete-source` is provided, source files are removed from S3 after zipping succeeds.
- If `--destination` is provided, temporary files and zip archives are stored in the specified directory; otherwise, the current working directory is used.
- Temporary working directories are cleaned up automatically.
