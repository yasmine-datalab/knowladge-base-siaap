"""ALL COMMON FUNCTIONS"""
from typing import List
import json
import io
import pathlib 
import json
import logging
from minio import Minio
import redis
from redis.commands.json import path


cred_file = pathlib.Path(__file__).parents[1] / "config/credentials.json"
if cred_file.exists():
    with cred_file.open("r",) as f:
        CONFIG = json.load(f)
else:
    raise RuntimeError("configs file don't exists")

config_file = pathlib.Path(__file__).parents[1] / "config/conf.json"
if config_file.exists():
    with config_file.open("r",) as f:
        CONFIG.update(json.load(f))
        
else:
    raise RuntimeError("configs file don't exists")


MINIO_CLIENT = Minio( endpoint= CONFIG["url"],
        access_key= CONFIG["accessKey"],
        secret_key= CONFIG["secretKey"]
        )

def save_files_minio(filename):
    """
    
    """
    logging.info("Starting to save files into Minio")
    found = MINIO_CLIENT.bucket_exists(CONFIG["bucket"])
    if not found:
        MINIO_CLIENT.make_bucket(CONFIG["bucket"])
        logging.info(f"{CONFIG['bucket'] } created")
    MINIO_CLIENT.fput_object(
            bucket_name= CONFIG["bucket"], object_name= filename, file_path= filename, content_type="application/json"
                            )






