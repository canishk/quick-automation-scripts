import boto3
import os
import logging
import shutil
import tempfile
import argparse
import time
import uuid
from botocore.exceptions import ClientError, NoCredentialsError

class S3Downloader:
    def __init__(self, bucket_name, main_folder=None, delete_source=False, destination=None):
        self.bucket_name = bucket_name
        self.main_folder = main_folder
        self.delete_source = delete_source
        self.destination = destination or os.getcwd()
        self.s3_client = boto3.client(
            's3'
        )
        logging.basicConfig(level=logging.INFO)

    def zip_s3_files(self, bucket_name, prefix, zip_file_path, delete_source=False):
        # Use a unique temp directory to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        temp_dir = os.path.join(self.destination, f'temp_download_{unique_id}')
        logging.info(f"Downloading files from bucket '{bucket_name}' with prefix '{prefix}' to temporary directory '{temp_dir}'...")
        try:
            # Create temp directory
            os.makedirs(temp_dir, exist_ok=True)
            
            # List objects in the specified S3 bucket and prefix
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if 'Contents' not in response:
                logging.warning(f"No files found in bucket '{bucket_name}' with prefix '{prefix}'")
                return

            downloaded_keys = []
            for obj in response['Contents']:
                file_key = obj['Key']
                # Skip if the key is just the prefix itself (folder marker)
                if file_key.rstrip('/') == prefix.rstrip('/'):
                    continue
                # Create subdirectories if needed
                relative_path = file_key[len(prefix):].lstrip('/')
                if not relative_path:
                    continue
                local_file_path = os.path.join(temp_dir, relative_path)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                logging.info(f"Downloading '{file_key}' to '{local_file_path}'...")
                
                # Download the file from S3 to the temporary directory
                self.s3_client.download_file(bucket_name, file_key, local_file_path)
                downloaded_keys.append(file_key)
                logging.info(f"Downloaded {file_key} to {local_file_path}")

            # Create a zip file from the downloaded files
            base_name = zip_file_path.replace('.zip', '')
            shutil.make_archive(base_name, 'zip', temp_dir)
            logging.info(f"Created zip file at {zip_file_path}")

            # Delete source files and folders in S3 after successful zip creation (optional)
            if delete_source or self.delete_source:
                s3_keys_to_delete = [obj['Key'] for obj in response['Contents']]
                if s3_keys_to_delete:
                    try:
                        self.s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={'Objects': [{'Key': key} for key in s3_keys_to_delete]}
                        )
                        logging.info(f"Deleted {len(s3_keys_to_delete)} source object(s) from bucket '{bucket_name}'")
                    except ClientError as e:
                        logging.error(f"Failed to delete source objects: {e}")

        except NoCredentialsError:
            logging.error("AWS credentials not found. Please provide valid credentials.")
        except ClientError as e:
            logging.error(f"An error occurred: {e}")
        except OSError as e:
            logging.error(f"File system error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        finally:
            # Clean up the temporary directory with retry
            for attempt in range(5):
                try:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                    break
                except OSError as e:
                    if attempt < 4:
                        logging.warning(f"Failed to clean up temp directory (attempt {attempt + 1}): {e}")
                        time.sleep(1)  # Wait before retrying
                    else:
                        logging.error(f"Failed to clean up temp directory after 5 attempts: {e}")

    def main(self):
        bucket_dir = os.path.join(self.destination, self.bucket_name)
        os.makedirs(bucket_dir, exist_ok=True)
        logging.info(f"Created directory '{bucket_dir}' for storing zip files.")
        try:
            logging.info(f"Connecting to S3 bucket '{self.bucket_name}'...")
            
            if self.main_folder:
                # Download from within the specified main folder
                # Ensure main_folder has a trailing slash for proper S3 prefix handling
                folder_prefix = self.main_folder if self.main_folder.endswith('/') else self.main_folder + '/'
                logging.info(f"Using main folder: '{folder_prefix}'")
                paginator = self.s3_client.get_paginator('list_objects_v2')
                
                root_has_files = False
                top_level_folders = []
                # List contents within the main folder
                for page in paginator.paginate(Bucket=self.bucket_name, Prefix=folder_prefix, Delimiter='/'):
                    if 'Contents' in page:
                        root_has_files = True
                    for common_prefix in page.get('CommonPrefixes', []):
                        top_level_folders.append(common_prefix['Prefix'])
                
                # if root_has_files:
                #     zip_file_path = os.path.join(self.bucket_name, f"{self.main_folder.strip('/')}_root.zip")
                #     self.zip_s3_files(self.bucket_name, folder_prefix, zip_file_path)
                logging.info(f"top level folders: {top_level_folders}")
                for folder in top_level_folders:
                    # Extract only the subfolder name without the main folder prefix
                    subfolder_name = folder[len(folder_prefix):].strip('/')
                    logging.info(f"Processing folder '{folder}'...")
                    zip_file_path = os.path.join(bucket_dir, f"{subfolder_name}.zip")
                    self.zip_s3_files(self.bucket_name, folder, zip_file_path, delete_source=self.delete_source)
            else:
                # Original behavior: download all top-level folders
                paginator = self.s3_client.get_paginator('list_objects_v2')
                
                root_has_files = False
                top_level_folders = []
                for page in paginator.paginate(Bucket=self.bucket_name, Delimiter='/'):
                    if 'Contents' in page:
                        root_has_files = True
                    for common_prefix in page.get('CommonPrefixes', []):
                        top_level_folders.append(common_prefix['Prefix'])
                
                if root_has_files:
                    zip_file_path = os.path.join(bucket_dir, f"{self.bucket_name}_root.zip")
                    self.zip_s3_files(self.bucket_name, '', zip_file_path, delete_source=self.delete_source)
                
                for folder in top_level_folders:
                    logging.info(f"Processing folder '{folder}'...")
                    zip_file_path = os.path.join(bucket_dir, f"{folder.strip('/')}.zip")
                    self.zip_s3_files(self.bucket_name, folder, zip_file_path, delete_source=self.delete_source)
        except NoCredentialsError:
            logging.error("AWS credentials not found. Please provide valid credentials.")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")


    
if __name__ == "__main__":
        parser = argparse.ArgumentParser(
            description="Download each top-level folder (and root files) from an S3 bucket as separate .zip files."
        )
        parser.add_argument('--bucket', help='Name of the S3 bucket')
        parser.add_argument('--folder', help='Main folder prefix within the bucket to download from (optional)')
        parser.add_argument('--delete-source', action='store_true', help='Delete downloaded files and folders from S3 after successful zip creation')
        parser.add_argument('--destination', help='Destination directory for temporary and zip files (default: current working directory)')
        args = parser.parse_args()
        if not args.bucket:
            logging.error("Bucket name is required. Use --bucket to specify the bucket name.")
            exit(1)
        downloader = S3Downloader(args.bucket, args.folder, delete_source=args.delete_source, destination=args.destination)
        downloader.main()
        
