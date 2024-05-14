import json
import fitz
from pathlib import Path
from minio import Minio
from io import BytesIO


def file_downloader(
    minio_client: Minio, bucket: str, filepath: str, outpath: Path = Path("/tmp")
):
    download_path = outpath / filepath
    minio_client.fget_object(bucket, filepath, str(download_path.absolute()))
    return download_path


def file_uploader(
    filepath: Path, minio_client: Minio, bucket: str, parent_folders: str = None
):
    if parent_folders is not None:
        object_name = f"{parent_folders}/{filepath.name}"
    else:
        object_name = filepath.name
    minio_client.fput_object(bucket, object_name, str(filepath))
    return object_name


def process_pdf_file(
    filepath: str,
    pdf: BytesIO ,
    #output_images_path: Path = Path("./images"),
    upload_images_to_minio: bool = False,
    minio_client: Minio = None,
    image_bucket: str = "images",
):
    output_dict = {
        "name": filepath.split("/")[-1],
        "path": filepath,
        "type": "TYPE",
        "rubrique": "RU",
        "extension": filepath.split("/")[-1].split(".")[-1],
        "spec_doc": False,
        "tags": [],
        "content": {"pages": []},
    }
    doc = fitz.open(stream=pdf, filetype="pdf") ## can replace by str
    for page_num, page in enumerate(doc, start=1):  # iterate the document pages
        page_data = {"id": page_num, "fulltext": "", "tables": [], "images": []}
        text_content = (
            page.get_text().encode("utf8").decode("utf-8")
        )  # get plain text (is in UTF-8)
        page_data.update({"fulltext": text_content})
        images_list = page.get_images()
        for image_index, img in enumerate(
            images_list, start=1
        ):  # enumerate the image list
            xref = img[0]  # get the XREF of the image
            pix = fitz.Pixmap(doc, xref)  # create a Pixmap

            if pix.n  < 4:  # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)
            # if pix.colorspace is not fitz.csRGB:
            #     pix = fitz.Pixmap(pix, fitz.csRGB)
            image_stream = BytesIO(pix.tobytes(output="png"))

            # img_path = Path(
            #      f'{output_dict.get("name")}_page_{page_num}-image_{image_index}.png'
            # )

            # img_path.unlink(missing_ok=True)  # Delete in case alreayd exists
            # img_path.mkdir(
            #     parents=True, exist_ok=True
            # )  # Create parents dirs it not existing
            #pix.save(image_stream)  # save the image as png
            image_stream.seek(0)

            # Upload the image to bucket
            # if upload_images_to_minio:
            #     img_fullpath = file_uploader(
            #         filepath=str(img_path),
            #         minio_client=minio_client,
            #         bucket=minio_bucket,
            #         parent_folders=str(img_path.parent),
            #     )
            #     page_data["images"].append(str(img_fullpath))
            # else:
            #     page_data["images"].append(str(img_path.absolute()))
            if not minio_client.bucket_exists(image_bucket):
                minio_client.make_bucket(image_bucket)
            name_without_space = output_dict["name"].replace(" ", "")
            image_name = f'{name_without_space}_page_{page_num}-image_{image_index}.png'
            result = minio_client.put_object(
            image_bucket,
            image_name,
            data=image_stream,
            length=image_stream.getbuffer().nbytes,
            content_type="image/png"
            )
            page_data["images"].append(str(result.object_name))
            pix = None
        tables = page.find_tables()
        for tab in tables:
            df = tab.to_pandas()
            tab_json_str = df.to_json()
            page_data["tables"].append(tab_json_str)
        output_dict["content"]["pages"].append(page_data)
    print(json.loads(json.dumps(output_dict)))
    return json.dumps(output_dict)


# if __name__ == "__main__":
#     # Read Config file
#     with open("./minio_credentials.json") as creds_file:
#         config_data = json.load(creds_file)
#         # print(config_data)

#     # Initiate connection with MinIO Server
#     client = Minio(
#         endpoint=config_data["url"],
#         access_key=config_data["accessKey"],
#         secret_key=config_data["secretKey"],
#         secure=config_data.get("secure", False),
#     )
#     BUCKET_NAME = "siaap-doe"
#     PROCESSED_BUCKET_NAME = "siaap-doe-processed"

#     # Download the file to be processed
#     infile = file_downloader(
#         minio_client=client,
#         bucket=BUCKET_NAME,
#         filepath="raw/FDSACID.PDF",
#         outpath=Path("/tmp"),
#     )
#     # infile = Path("data/datatest/1115 00x00-00 000000 Eq Lis 001 PDR INSTRM DOE.pdf")
#     result = process_pdf_file(
#         filepath=infile,
#         upload_images_to_minio=True,
#         minio_client=client,
#         minio_bucket=PROCESSED_BUCKET_NAME,
#         output_images_path=Path("data/processed/images"),
#     )

#     # Write result to a file
#     with open("sample_output_2.json", "w") as outfile:
#         outfile.write(result)

#     print(result)
