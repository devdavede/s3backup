# S3 Backup Utility

This Python script provides automated backup functionalities for files and MySQL databases to an AWS S3 bucket. Below is a brief overview of its features and how to use it.

## Features

- **Backup Files**: Easily backup files to an AWS S3 bucket.
- **Backup MySQL Databases**: Option to backup MySQL databases and store them in the S3 bucket.
- **Encryption**: Supports encryption of files before uploading them to S3 for added security.
- **Delete Deprecated Files**: Removes old versions of files from the S3 bucket to maintain space efficiency.
- **Download Files**: Capability to download files and folders from the S3 bucket.

## Setup

1. **Install Dependencies**: Ensure you have the required dependencies installed. You can install them using pip:

    ```bash
    pip install boto3 tinydb cryptography
    ```

2. **Configuration**:
    - Update the variables in the script according to your setup. Modify the `entities`, `bucketname`, `db_path`, `crypto`, `crypto_key_file`, `aws_access_key_id`, `aws_secret_access_key`, `region_name`, `backup_databases`, `mysql_username`, `mysql_password`, `mysql_tmp_dump_file`, and `s3_mysql_dump_path` variables to match your environment.
    - Ensure you have appropriate AWS credentials configured either via environment variables or AWS config files.

3. **Encryption Key Setup**:
    - If encryption (`crypto`) is enabled, ensure to provide a valid key file (`crypto_key_file`). If the file doesn't exist, the script will prompt you to create a new one.

## Notes

- Ensure proper configuration and permissions are set to interact with AWS services.
- Use caution while performing operations like deleting old versions of files as it can't be undone.
- For any issues or inquiries, refer to the provided contact information or seek support from the relevant channels.
- I assume no liability for this script. Use with caution.
- See [Auto-Backup to Amazon S3 on devdave.de](https://devdave.de/2021/12/auto-backup-to-amazon-s3/) for more details.

