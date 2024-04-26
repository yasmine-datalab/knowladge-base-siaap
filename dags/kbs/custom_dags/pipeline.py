# from datetime import datetime
# from minio import Minio
# from airflow.operators.python import PythonOperator
# from airflow.sensors.python import PythonSensor
# from airflow.models import Variable
# from airflow import DAG
# from kbs import CONFIG
# from kbs.common.rw import read_files, push_in_redis

# ### Uses dynamic task

# def from_minio_to_redis():
#     """"
    
#     """
#     objects = read_files(["json"])
#     if objects:
#         push_in_redis(objects)


# with DAG(
#         'pipeline',
#         default_args={
#             'depends_on_past': False,
#             'wait_for_downstream': False,
#            # 'email': CONFIG["airflow_receivers"],
#             'email_on_failure': True,
#             'email_on_retry': False,
#             'max_active_run': 1,
#             'retries': 0
#         },
#         description='LOAD DATA FROM MINIO TO REDIS AND FROM REDIS TO NEO4J',
#         schedule_interval=None,
#         start_date=datetime(2024, 3, 1, 0, 0, 0),
#         catchup=True
# ) as dag:
#     loadinredis = PythonOperator(
#                 task_id='load_in_redis',
#                 provide_context=True,
#                 python_callable=from_minio_to_redis,
#                 #on_failure_callback=on_failure,
#                 op_kwargs={
#                 },
#                 dag=dag,
#                         )
    
#     loadinredis