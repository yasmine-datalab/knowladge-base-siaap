import logging
from typing import List
import json
import io
from minio import Minio
import redis
from redis.commands.json import path
from neo4j import GraphDatabase
#from kbs import CONFIG

# REDIS_CLIENT = redis.Redis(
#     host=CONFIG["redisHost"], port=CONFIG["redisPort"], db=0
#    )

# MINIO_CLIENT = Minio( endpoint= CONFIG["url"],
#         access_key= CONFIG["accessKey"],
#         secret_key= CONFIG["secretKey"]
#         )

REDIS_CLIENT = redis.Redis(
    host= "127.0.0.1", port= 6379, db=0
   )

MINIO_CLIENT = Minio( endpoint= "viable-gnat-enormous.ngrok-free.app",
        access_key= "X8IFd1Ew33jXamOEVGZa",
        secret_key= "tRQ4Yd8j7ykJ29dfKabmretrcFryHQIuqCMGvDvB"
        )




def read_files(bucket, prefix=None, extensions: List[str] = None) -> List[str]:
    """
    Get a list of names of all files in the bucket that match the given prefix and extensions.
    Args:
        client: Minio client object
        bucket: Name of the bucket to search in
        prefix: Prefix to filter the files by
        extensions: List of extensions to filter the files by
    Returns: 
        List of names of all files that match the given criteria
    """
    logging.info("start to get objects in minio")
    extensions = ['.json'] if extensions is None else [ext.lower() for ext in extensions]  
    logging.info("get objects")
    # objects = MINIO_CLIENT.list_objects(CONFIG["bucket"],recursive=True)
    objects = MINIO_CLIENT.list_objects(bucket, prefix, recursive=True)
    logging.info("get good objects")

    if not objects:
        raise RuntimeError(f"No file found")
    good_objects = [obj.object_name for obj in objects if obj.object_name.lower().endswith(tuple(extensions)) ]
    if not good_objects:
        raise ValueError(f"No files found with good extensions {extensions}")
    return good_objects
  

def push_in_redis(objects):
    """ """ 
    logging.info("start to push data in redis")
    for obj in objects:
        #file = MINIO_CLIENT.get_object(CONFIG["bucket"], obj)
        file = MINIO_CLIENT.get_object("extracted", obj)
        data = json.load(io.BytesIO(file.data))
        print(data)
        #REDIS_CLIENT.json().set(obj.split()[-1], path.Path.root_path(), data)
    
        print(f"{obj.split()[-1]} in redis")

def load_from_redis(ids):
    """
    """
    data = []
    for id in ids:
        response=REDIS_CLIENT.execute_command('JSON.GET', id)
        data.append(json.loads(response))
    return data


def save_files_minio(data, filename, bucket):
    """
    
    """
    logging.info("Starting to save files into Minio")
    found = MINIO_CLIENT.bucket_exists(bucket)
    if not found:
        MINIO_CLIENT.make_bucket(bucket)
        logging.info(f"{bucket} created")
    if isinstance(data, dict):
        serialize_data = json.dumps(data)
        MINIO_CLIENT.put_object(
        bucket_name=bucket,
        object_name=filename,
        data=io.BytesIO(serialize_data.encode('utf-8')),
        length=len(serialize_data),
        content_type='application/json'
    )
    
    # MINIO_CLIENT.put_object(
    #         bucket_name= bucket, object_name= filename, file_path= filename, content_type="application/json")

# a  = read_files("intervalles")
# print(a)
# for obj in a:
#     MINIO_CLIENT.remove_object('intervalles',obj)
#     print(obj)

for obj in MINIO_CLIENT.list_objects('siaap-doe', recursive=True):
    print(f"{obj.object_name}....{obj.last_modified}")
