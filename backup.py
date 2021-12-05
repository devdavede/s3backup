import logging
import boto3
from botocore.exceptions import ClientError
import os
from glob import glob
from tinydb import TinyDB
import hashlib
from tinydb import Query
import tinydb
import os.path
from tinydb import where
from cryptography.fernet import Fernet
import uuid
import sys

entities = ["", "", ""]
bucketname = "backup.51.75.69.218"
db_path = 's3backup.hashes.json'

crypto = False
crypto_key_file = '/root/s3backup.key'

aws_access_key_id = None
aws_secret_access_key = None
region_name = None

backup_databases = True
mysql_username = None
mysql_password = None
mysql_tmp_dump_file = '/tmp/mysql.dump'
s3_mysql_dump_path = 'mysql.dump.sql'

db = TinyDB(db_path)

s3_client = None

if aws_access_key_id is None or aws_secret_access_key is None or region_name is None:
    s3_client = boto3.client('s3')
else:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name)

def keymanagement():
    if crypto is False: return
    global crypto_key
    if not os.path.isfile(crypto_key_file): 
        key = Fernet.generate_key()
        with open(crypto_key_file, "wb") as kf: kf.write(key)
    crypto_key = open(crypto_key_file, "rb").read()

def upload_file(file_name, bucket_path = None):
    if bucket_path is None: bucket_path = file_name
    if crypto is True:
        tmpFileName = hashlib.md5(file_name.encode('utf-8')).hexdigest()
        with open(file_name, "rb") as file:
            file_data = file.read()
            encrypted_data = Fernet(crypto_key).encrypt(file_data)
        with open(tmpFileName, "wb") as file: file.write(encrypted_data)
        file_name = tmpFileName
    try:
        response = s3_client.upload_file(file_name, bucketname, bucket_path)
    except ClientError as e:
        raise Exception(e)
    finally:
        if crypto: os.remove(tmpFileName)

def download(path, needConfirmation = False):
    if needConfirmation is True:
        print("Download all files and folders within '%s'?" % path)
        userinput = input("Press Y to continue\r\n")
        if userinput != "Y" and userinput != "y":
            print("Abort")
            return
        for key in s3_client.list_objects(Bucket=bucketname)['Contents']:
            file=key['Key']
            if file.startswith(path):
                s3_client.download_file(bucketname, file, file)
                print("Download: %s " % file)
                if crypto is True:
                    f = Fernet(crypto_key)
                    with open(file, "rb") as fileHandle: encrypted_data = fileHandle.read()
                    decrypted_data = f.decrypt(encrypted_data)
                    with open(file, "wb") as file: file.write(decrypted_data)

def mysql_dump():
    if backup_databases is False: return
    print("Backup Database")
    if mysql_username is not None and mysql_password is not None:
        os.system('mysqldump -u %s -p%s --all-databases > %s' % (mysql_username, mysql_password, mysql_tmp_dump_file))
    else:
        os.system('mysqldump -u root --all-databases > %s' % (mysql_tmp_dump_file))

    print(mysql_tmp_dump_file)
    if not os.path.isfile(mysql_tmp_dump_file): raise Exception('Could not dump database')

    upload_file(mysql_tmp_dump_file, s3_mysql_dump_path)
    os.remove(mysql_tmp_dump_file)
    print("Done")

def delete_old_versions():
    print("Delete deprecated files")
    for key in s3_client.list_objects(Bucket=bucketname)['Contents']:
        file=key['Key']
        for entity in entities:
            if file.startswith(entity) and not os.path.isfile(file):
                print("Delete '" + file + "' from bucket")
                s3_client.delete_object(Bucket=bucketname, Key=file)
                db.remove(where('file') == file)
    print("Done")
    
def backup_entity(path):
    if path.endswith('/'): path = path[:-1]
    if os.path.isdir(path):
        for sub in os.listdir(path): backup_entity(path + "/" + sub)
    elif os.path.isfile(path):
        hash = hashlib.md5(open(path,'rb').read()).hexdigest()
        file_db = db.get(Query().file == path)
        if file_db is None or file_db['hash'] != hash:
            print("Backup: %s" % path)
            upload_file(path)
            db.upsert({'hash': hash, 'file': path}, Query().file == path)
    else:
        print("File %s does not exist but is specified in the entities array" % path)

def backup():
    print("Backup files")
    for entity in entities: backup_entity(entity)        
    print("Done")

def main():
    keymanagement()
    print(len(sys.argv))
    if (len(sys.argv) == 3) and sys.argv[1] == "download":
        download(sys.argv[2], True)
    else:
        print("Debug tool running")
        mysql_dump()
        delete_old_versions()
        backup()
        print("Finished all debug tasks")

if __name__ == "__main__":
    main()
