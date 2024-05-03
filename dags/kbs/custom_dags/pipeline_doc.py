from __future__ import annotations
from typing import List
import io
from datetime import datetime
import pandas as pd
import logging
import json
from minio import Minio
import redis
from redis.commands.json import path
import uuid
from airflow.decorators import task, dag
from airflow.models.dag import DAG
from airflow.models import Variable
from kbs.common.rw import save_files_minio, read_files
from kbs.common.script_extraction import extract
from kbs.common.pdf_processor import process_pdf_file



REDIS_HOST = Variable.get("REDIS_HOST")
REDIS_PORT = Variable.get("REDIS_PORT")
MINIO_ENDPOINT = Variable.get("MINIO_ENDPOINT")
MINIO_ACCESS_KEY= Variable.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = Variable.get("MINIO_SECRET_KEY")


REDIS_CLIENT = redis.Redis(
    host= REDIS_HOST, port= REDIS_PORT, db=1
   )

# MINIO_CLIENT = Minio( endpoint= "viable-gnat-enormous.ngrok-free.app",
#         access_key= "X8IFd1Ew33jXamOEVGZa",
#         secret_key= "tRQ4Yd8j7ykJ29dfKabmretrcFryHQIuqCMGvDvB"
#         )
MINIO_CLIENT = Minio(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=False)

default_args = {
    'start_date': datetime(2024, 3, 1),
    'depends_on_past': True
}

@dag(dag_id= "pipeline_doc", default_args= default_args, catchup=True, schedule_interval=None)
    
def docs_process():
    """"""
    @task
    def gen_dates(exec_date):
        """ """
        #dates = {"start": exec_date.split(".")[0], "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S") }
        dates = {"start": "2023-03-01 00:00:00", "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S") } # first launch
        filename = f"dates_{exec_date.split()[0].replace('-', '')}"
        save_files_minio(MINIO_CLIENT, dates, filename+".json", "intervalles")
        return filename


    @task
    def read_docs(date_prefix) -> List[str]:
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
        logging.info("get date")
        dates_files = read_files(MINIO_CLIENT, bucket="intervalles", prefix=date_prefix)
        if not dates_files:
            raise FileExistsError("No date file found")
        
        file = MINIO_CLIENT.get_object("intervalles", dates_files[0])
        intervals = json.load(io.BytesIO(file.data))
        logging.info(f"intervals is {intervals}")
        logging.info("start to get objects in minio")
        extensions = ['.pdf'] 
        # objects = MINIO_CLIENT.list_objects(CONFIG["bucket"],recursive=True)
        #objects = read_files(minio_client=MINIO_CLIENT,bucket= 'siaap-doe',intervals=intervals, extensions=extensions )
        objects = MINIO_CLIENT.list_objects("siaap-doe",recursive=True)
        if not objects:
            raise RuntimeError(f"No file found")
        #good_objects = [obj.object_name for obj in objects if obj.object_name.lower().endswith(tuple(extensions)) and datetime.strptime(intervals["start"], "%Y-%m-%d %H:%M:%S")<obj.last_modified.replace(tzinfo=None, microsecond=0) <=  datetime.strptime(intervals["end"], "%Y-%m-%d %H:%M:%S") ]
        for obj in objects:
            print(obj.object_name)
        #return good_objects
    
    @task
    def push_in_redis(obj):
        """ """ 
        logging.info("start to push data in redis")
        #file = MINIO_CLIENT.get_object(CONFIG["bucket"], obj)
        file = MINIO_CLIENT.get_object('siaap-doe', obj)
        file_in_bio = io.BytesIO(file.data)
        if obj.lower().endswith((".pdf")):
            data = process_pdf_file(obj, file_in_bio, True, MINIO_CLIENT, "images")
        #if obj.lower().endswith(".pdf"):
        elif obj.lower().endswith((".xls", "xlsx")):

            data = json.load(io.BytesIO(file.data))
        else:
            data = json.load(io.BytesIO(file.data))
        key = str(uuid.uuid1)
        REDIS_CLIENT.json().set(key, path.Path.root_path(), data)
        logging.info(f"{obj.split()[-1]} in redis")

    date_prefix = gen_dates("{{execution_date}}")
    objects = read_docs(date_prefix)
    push_in_redis.expand(obj=objects)
    
    

pipeline_equipement = docs_process()