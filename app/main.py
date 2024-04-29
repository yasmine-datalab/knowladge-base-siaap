from typing import List, Dict, Optional
import requests
from fastapi import FastAPI, Body
from fastapi.exceptions import HTTPException 
import json
from utils import save_files_minio

app = FastAPI()
URL = "http://localhost:8080/api/v1/dags/pipeline/dagRuns"

# @app.post("/fileupload")
# def upload(files: List[UploadFile]=List[None]):
#     """"
    
#     """
#     if files:
#         good_files = [file for file in files if file.content_type == "application/json"]
#         if not good_files:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "No json file uploaded" )
#         for file in good_files:
#             try:
#                 data = json.loads(file.file.read())
#                 with open (file.filename, "w") as f:
#                     json.dump(str(data), f)
#                 save_files_minio(file.filename)
#             except Exception as e :
#                 return {"message": f"{e}"}
#     headers = {
#     'accept': 'application/json',
#     'Content-Type': 'application/json',
# }
#     conf = {
#         "conf": {},
#         "dag_run_id": "string",}
#     response = requests.post(URL, json=conf, timeout=300, auth = ('admin', '8bAR3UrxTN3EtySF'), headers=headers)
#     print(response)
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail="Failed to trigger DAG")
#     return {"message": f"Successfully uploaded {[file.filename for file in files]}"}

@app.post("/save")
async def save(data: Optional[Dict] = Body(default=None)):
    """
    """
    if data is None:
        
    else:



