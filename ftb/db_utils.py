import os
import time
import json
import uuid
import boto3
import bcrypt
import shutil
import certifi
import tempfile
import warnings 

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal
from pymongo import MongoClient
from flask import send_file
"""=========== PERMISSIONS ================================================================"""

user_types = Literal[
    "ftb_field_tester",
    "ftb_engineer",
    "ftb_admin",
]


def get_mongo_un(user_type):
    # TODO: error handling if none of above
    return os.environ.get("ftbMongoUN", None)


def get_mongo_pw(user_type):
    # TODO: error handling if none of above
    return os.environ.get("ftbMongoPW", None)


def getAWSAccessKey(user_type):
    # TODO: error handling if none of above
    # TODO: ftb_engineer and ftb_field_tester key management!!!
    if user_type == "ftb_field_tester":
        return os.environ.get("ftb_field_tester_AWSAccessKey", None)
    elif user_type == "ftb_engineer":
        return os.environ.get("ftb_engineer_AWSAccessKey", None)
    elif user_type == "ftb_admin":
        return os.environ.get("ftb_admin_AWSAccessKey", None)


def getAWSSecretKey(user_type):
    # TODO: error handling if none of above
    if user_type == "ftb_field_tester":
        return os.environ.get("ftb_field_tester_AWSSecretKey", None)
    elif user_type == "ftb_engineer":
        return os.environ.get("ftb_engineer_AWSSecretKey", None)
    elif user_type == "ftb_engineer" or user_type == "ftb_admin":
        return os.environ.get("ftb_admin_AWSSecretKey", None)


"""=========== GENERIC DB UTILITIES ================================================================"""


def access_mongo_collection(db_name, cl_name, user_type):
    client_name = (
        "mongodb+srv://"
        + get_mongo_un(user_type)
        + ":"
        + get_mongo_pw(user_type)
        + "@clientdata.3mjy7ss.mongodb.net/"
    )
    cluster = MongoClient(client_name, tlsCAFile=certifi.where())
    db = cluster[db_name]
    collection = db[cl_name]
    return collection


def create_boto3_client(user_type):
    s3 = boto3.resource(
        service_name="s3",
        region_name="us-west-2",
        aws_access_key_id=getAWSAccessKey(user_type),
        aws_secret_access_key=getAWSSecretKey(user_type),
    )
    return s3


def mongo_make_post(metadata: dict, db_name, cl_name, user_type):
    collection = access_mongo_collection(db_name, cl_name, user_type)
    if collection.find_one({"_id": metadata["_id"]}):
        # TODO: test
        warnings.warn(f"Document with the _id {metadata['_id']} already exists. No new document created.", UserWarning)
    else:
        collection.insert_one(metadata)


def get_document(query_by: str, id: str, db: str, cl: str, user_type: str):
    collection = access_mongo_collection(db, cl, user_type)
    document = collection.find_one({query_by: id})
    return document


def delete_many(
    query_by: str, id: str, db: str, cl: str, user_type: str
):
    if user_type == "ftb_engineer" or user_type == "ftb_admin":
        db = "fieldTestDB"
        col = "fieldTestMD"
    else:
        # TODO: tet
        warnings.warn("Permission Denied: user does not have delete_many permissions.", UserWarning)
        return False

    collection = access_mongo_collection(db, cl, user_type)
    s3_success = None
    num_to_delete = 0
    if cl == col and db == db:
        metadata = list(collection.find({query_by: id}))
        num_to_delete = len(metadata)
        s3 = create_boto3_client(user_type)
        for item in metadata:
            s3_success = s3.Object("fieldtestbuddy", item["filename"]).delete()  #TODO maybe?: Expecteuser_dbcketOwner="616163632496"

    mongo_success = collection.delete_many({query_by: id})

    if num_to_delete == 0 and cl == col:
        print("No items match query, nothing deleted")
        return True
    if num_to_delete != mongo_success.deleted_count and cl == col:
        warnings.warn("Warning: number deleted did not match query results, check database.", UserWarning)
        return False
    if num_to_delete == mongo_success.deleted_count and s3_success is not None:
        return True


def update_many(update_field: str, update_val: str, db: str, cl: str, user_type):
    collection = access_mongo_collection(db, cl, user_type)
    mongo_success = collection.update_many({}, {"$set": {update_field: update_val}})
    return mongo_success


"""=========== FIELD TEST DB =========================================================================="""


# field test variables
ft_db = "fieldTestDB"  # TODO: no hardcode
cl_db = "fieldTestMD"  # TODO: no hardcode
bucketName = "fieldtestbuddy"


# TODO: Filetype expansion???
def upload_many(filepath, post_data, user_type):
    filepath = Path(filepath)
    files = (
        list(filepath.glob("*.bin"))
        + list(filepath.glob("*.csv"))
        + list(filepath.glob("*.xls"))
    )
    for i, file in enumerate(files):
        upload_one(filepath, file.name, post_data[i], user_type)


def upload_one(filepath: str, filename: str, metadata: dict, user_type):
    post_UUID = str(uuid.uuid4())
    unix_upload = int(time.time())
    uuid_filename = (
        post_UUID + filename[-4:]
    )  # TODO: this assumes extension is three chars (bin, csv, xls, etc.)

    metadata.update(
        {
            "_id": post_UUID,
            "filename": uuid_filename,
            "uploadTimestamp": unix_upload,
        }
    )

    mongo_make_post(metadata, ft_db, cl_db, user_type)
    os.rename(Path(filepath, filename), Path(filepath, uuid_filename))
    try:
        _ftb_bucket_upload(filepath, uuid_filename, user_type)
    finally:
        os.rename(Path(filepath, uuid_filename), Path(filepath, filename))


def _ftb_bucket_upload(filepath, filename, user_type):
    # TODO:
    #  - Test functionality for failed upload
    #  - Check what happens when you try to upload something that is already in the bucket!!!
    s3 = create_boto3_client(user_type)
    ftb_bucket = s3.Bucket(name=bucketName)
    ftb_bucket.upload_file(Path(filepath, filename), filename)


# def get_ftb_field_test(field_test_name: str, user_type):
#     (tmp_dir, query_metadata) = ftb_download("field_test_name", field_test_name, user_type)
#     return (tmp_dir, query_metadata)


# def getftbTrail(trailName: str, user_type):
#     (tmp_dir, query_metadata) = ftb_download("trailName", trailName, user_type)
#     return (tmp_dir, query_metadata)


def download(query_by: str, key: str, user_type, app_dir):
    collection = access_mongo_collection(ft_db, cl_db, user_type)
    query = {query_by: {"$regex": f".*{key}.*"}} # works with partial matching!
    query_metadata = list(collection.find(query))

    # now pull file from s3 bucket
    s3 = create_boto3_client(user_type)
    ftb_bucket = s3.Bucket(name=bucketName)

    # create directory
    tmp_dir = Path(app_dir, "tmp_{}".format(int(time.time())))
    # tmp_dir = Path(curdir, "tmp") #TODO may need debug
    tmp_dir.mkdir(exist_ok=True)

    # create field test subdirectories
    field_tests = set([item["fieldTestName"] for item in query_metadata])
    for field_test_name in field_tests:
        # create field test subdir
        test_dir = Path(tmp_dir, field_test_name)
        test_dir.mkdir(exist_ok=True)

        # dump metadata to ft folder
        ft_level_md = [
            item for item in query_metadata if item["fieldTestName"] == field_test_name
        ]
        md_filename = field_test_name + "_metadata.json"
        json_filepath = Path(test_dir, md_filename)
        with open(json_filepath, "w") as outfile:
            json.dump(ft_level_md, outfile)

    for item in query_metadata:
        download_path = Path(app_dir, item["filename"])
        ftb_bucket.download_file(item["filename"], download_path)
        # put file in appropriate field test subdirectory
        Path(app_dir, item["filename"]).rename(
            Path(tmp_dir, item["fieldTestName"], item["filename"])
        )

    # store metadata in local json file
    json_filepath = Path(tmp_dir, "metadata.json")
    with open(json_filepath, "w") as outfile:
        json.dump(query_metadata, outfile)

    # TODO: will this work when hosted elsewhere???
    shutil.make_archive(str(tmp_dir), "zip", root_dir=tmp_dir)
    shutil.rmtree(tmp_dir)
    print("archive name: ", tmp_dir)
    zip_name = str(tmp_dir) + ".zip"
    return zip_name


def exact_match_query(query_by: str, search_string: str, user_type):
    collection = access_mongo_collection(ft_db, cl_db, user_type)
    query_metadata = list(collection.find({query_by: search_string}))
    return query_metadata

def partial_match_query(query_by: str, searchString: str, user_type):
    collection = access_mongo_collection(ft_db, cl_db, user_type)
    query = {query_by: {"$regex": f".*{searchString}.*"}}

    query_metadata = list(collection.find(query))
    return query_metadata


def get_unique_field_names(user_type: str):
    collection = access_mongo_collection(ft_db, cl_db, user_type)
    pipeline = [
        {"$project": {"fields": {"$objectToArray": "$$ROOT"}}},
        {"$unwind": "$fields"},
        {"$group": {"_id": None, "uniqueFields": {"$addToSet": "$fields.k"}}},
    ]

    # Execute the pipeline
    result = collection.aggregate(pipeline)

    # Extract the unique field names from the result
    distinct_fields = result.next()["uniqueFields"]

    distinct_fields.remove("_id")
    return distinct_fields


"""=========== FRONT END DB =========================================================================="""

fe_db = "frontEndDB"
fe_cl = "metadataDefinition"


def md_def_upload(data: dict, user_type):
    post_UUID = str(uuid.uuid4())  # this will be the "_id" for the document
    unix_upload = int(time.time())
    data.update({"uploadTimestamp": unix_upload})
    data.update({"_id": post_UUID})
    mongo_make_post(data, fe_db, fe_cl, user_type)


def get_md_def(fieldTestType, user_type):
    collection = access_mongo_collection(fe_db, fe_cl, user_type)
    md_definition = collection.find_one({"fieldTestType": fieldTestType})
    return md_definition


def get_field_test_types(user_type):
    collection = access_mongo_collection(fe_db, fe_cl, user_type)
    fieldTestTypes = collection.distinct("fieldTestType")
    return fieldTestTypes


"""=========== USER DB =========================================================================="""


user_db = "userDB"
user_cl = "users"


def user_db_upload(data: dict, user_type):
    post_UUID = str(uuid.uuid4())  # this will be the "_id" for the document
    unix_upload = int(time.time())
    data.update({"uploadTimestamp": unix_upload})
    data.update({"_id": post_UUID})
    mongo_make_post(data, user_db, user_cl, user_type)


def get_user(un: str, user_type: str):
    collection = access_mongo_collection("userDB", "users", user_type)
    user = collection.find_one({"userName": un})
    return user


def create_user_dict(un, pw: str, name: str, org: str, user_type: str, email: str):
    pw_hash = bcrypt.hashpw(str.encode(pw), bcrypt.gensalt()).decode("utf-8")
    return dict(
        userName=un,
        password=pw_hash,
        name=name,
        org=org,
        user_type=user_type,
        email=email,
    )


def update_user(query_by: str, key: str, update_field: str, update_val: str, user_type):
    # if it's a password, hash it
    if update_field == "password":
        update_val = bcrypt.hashpw(update_val, bcrypt.gensalt()).decode("utf-8")

    collection = access_mongo_collection(user_db, user_cl, user_type)
    mongo_success = collection.update_one(
        {query_by: key}, {"$set": {update_field: update_val}}
    )
    return mongo_success


def update_user_pw(un, pw, user_type):
    pw_hash = bcrypt.hashpw(str.encode(pw), bcrypt.gensalt()).decode("utf-8")
    return update_user(
        query_by="username",
        key=un,
        update_field="password",
        update_val=pw_hash,
        user_type=user_type,
    )
