import os
import time
import json
import uuid
import boto3
import shutil
import certifi

from pathlib import Path
from pymongo import MongoClient

"""=========== PERMISSIONS ================================================================"""


def getMongoUN(userType="casslabsadmin"):
    if (
        userType == "ftb_field_tester"
        or userType == "ftb_engineer"
        or userType == "ftb_admin"
    ):
        return os.environ.get("ftbMongoUN", None)
    elif userType == "casslabsadmin":
        return os.environ.get("cassLabsMongoUN", None)
    # TODO: error handling if none of above


def getMongoPW(userType):
    # we can set user type in the user object baby
    if (
        userType == "ftb_field_tester"
        or userType == "ftb_engineer"
        or userType == "ftb_admin"
    ):
        return os.environ.get("ftbMongoPW", None)
    elif userType == "casslabsadmin":
        return os.environ.get("cassLabsMongoPW", None)
    # TODO: error handling if none of above


def getAWSAccessKey(userType):
    # we can set user type in the user object baby
    if userType == "ftb_field_tester":
        return os.environ.get("ftb_field_tester_AWSAccessKey", None)
    elif userType == "ftb_admin" or userType == "ftb_engineer":
        return os.environ.get("ftb_admin_AWSAccessKey", None)
    elif userType == "casslabsadmin":
        return os.environ.get("cassLabsAWSAccessKey", None)
    # TODO: error handling if none of above


def getAWSSecretKey(userType):
    # we can set user type in the user object baby
    if userType == "ftb_field_tester":
        return os.environ.get("ftb_field_tester_AWSSecretKey", None)
    elif userType == "ftb_engineer" or userType == "ftb_admin":
        return os.environ.get("ftb_admin_AWSSecretKey", None)
    elif userType == "casslabsadmin":
        return os.environ.get("cassLabsAWSSecretKey", None)
    # TODO: error handling if none of above


"""=========== GENERIC DB UTILITIES ================================================================"""


def accessMongoCollection(databaseName, collectionName, userType):
    if (
        userType == "ftb_field_tester"
        or userType == "ftb_admin"
        or userType == "ftb_engineer"
    ):
        clientName = (
            "mongodb+srv://"
            + getMongoUN(userType)
            + ":"
            + getMongoPW(userType)
            + "@clientdata.3mjy7ss.mongodb.net/"
        )
    elif userType == "casslabsadmin":
        clientName = (
            "mongodb+srv://"
            + getMongoUN(userType)
            + ":"
            + getMongoPW(userType)
            + "@casslogger.atyux9l.mongodb.net/?retryWrites=true&w=majority"
        )
    cluster = MongoClient(clientName, tlsCAFile=certifi.where())
    db = cluster[databaseName]
    collection = db[collectionName]
    return collection


def createBoto3Client(userType):
    s3 = boto3.resource(
        service_name="s3",
        region_name="us-west-2",
        aws_access_key_id=getAWSAccessKey(userType),
        aws_secret_access_key=getAWSSecretKey(userType),
    )
    return s3


def mongoMakePost(metadata: dict, databaseName, collectionName, userType):
    collection = accessMongoCollection(databaseName, collectionName, userType)
    if collection.find_one({"_id": metadata["_id"]}):
        print("WARNING! Document exists, none created!")
        # raise warnings.warn("Document with the _id ")
    else:
        collection.insert_one(metadata)


def getDocument(queryBy: str, id: str, myDatabase: str, myCollection: str, userType):
    collection = accessMongoCollection(myDatabase, myCollection, userType)
    document = collection.find_one({queryBy: id})
    return document


def deleteMany(queryBy: str, id: str, myDatabase: str, myCollection: str, userType):
    if userType == "ftb_engineer" or userType == "ftb_admin":
        db = "fieldTestDB"
        col = "fieldTestMD"
    elif userType == "casslabsadmin":
        db = "fieldTestDB"
        col = "fieldTestMD"
    else:
        print("Permission Denied")
        return False

    collection = accessMongoCollection(myDatabase, myCollection, userType)
    s3Success = None
    numToDelete = 0
    if myCollection == col and myDatabase == db:
        metadata = list(collection.find({queryBy: id}))
        numToDelete = len(metadata)
        s3 = createBoto3Client(userType)
        for item in metadata:
            s3Success = s3.Object(
                "fieldtestbuddy", item["filename"]
            ).delete()  # ehhhh ExpectedBucketOwner="616163632496"

    mongoSuccess = collection.delete_many({queryBy: id})

    if numToDelete == 0 and myCollection == col:
        print("No items match query, nothing deleted")
        return True
    if numToDelete != mongoSuccess.deleted_count and myCollection == col:
        print("Error: items deleted does not equal number queried")
        return False
    if numToDelete == mongoSuccess.deleted_count and s3Success is not None:
        return True
    return True


def updateMany(
    queryBy: str,
    key: str,
    myDatabase: str,
    myCollection: str,
    updateField: str,
    updateVal: str,
    userType,
):
    collection = accessMongoCollection(myDatabase, myCollection, userType)
    mongoSuccess = collection.update_many({}, {"$set": {updateField: updateVal}})
    return mongoSuccess


"""=========== FIELD TEST DB =========================================================================="""


# field test variables
dbFT = "fieldTestDB"  # TODO: no hardcode
colFT = "fieldTestMD"  # TODO: no hardcode
bucketName = "fieldtestbuddy"

# POST FUNCTIONs


# TODO: Filetype expansion???
def ftbDbUploadBulk(filepath, postData, userType):
    filepath = Path(filepath)
    files = (
        list(filepath.glob("*.bin"))
        + list(filepath.glob("*.csv"))
        + list(filepath.glob("*.xls"))
    )
    for i, file in enumerate(files):
        print(file.name)
        ftbDbUpload(filepath, file.name, postData[i], userType)


def ftbDbUpload(filepath: str, filename: str, metadata: dict, userType):
    postUUID = str(uuid.uuid4())
    unixUpload = int(time.time())
    uuidFilename = (
        postUUID + filename[-4:]
    )  # TODO: this assumes extension is three chars (bin, csv, xls, etc.)

    metadata.update(
        {
            "_id": postUUID,
            "filename": uuidFilename,
            "uploadTimestamp": unixUpload,
        }
    )

    mongoMakePost(metadata, dbFT, colFT, userType)
    os.rename(Path(filepath, filename), Path(filepath, uuidFilename))
    try:
        _ftbBucketUpload(filepath, uuidFilename, userType)
    finally:
        os.rename(Path(filepath, uuidFilename), Path(filepath, filename))


def _ftbBucketUpload(filepath, filename, userType):
    # UPLOAD FILES TO BUCKET
    # TODO:
    #  - Test functionality for failed upload
    #  - Check what happens when you try to upload something that is already in the bucket!!!
    s3 = createBoto3Client(userType)
    ftb_bucket = s3.Bucket(name=bucketName)
    ftb_bucket.upload_file(Path(filepath, filename), filename)


# QUERYING FUNCTIONS


def getftbFieldTest(fieldTestName: str, userType):
    (tmpDir, queryMetadata) = ftbQuery("fieldTestName", fieldTestName, userType)
    return (tmpDir, queryMetadata)


def getftbTrail(trailName: str, userType):
    (tmpDir, queryMetadata) = ftbQuery("trailName", trailName, userType)
    return (tmpDir, queryMetadata)


def ftbQuery(queryBy: str, key: str, userType):
    collection = accessMongoCollection(dbFT, colFT, userType)
    queryMetadata = list(collection.find({queryBy: key}))

    # now pull file from s3 bucket
    s3 = createBoto3Client(userType)
    ftb_bucket = s3.Bucket(name=bucketName)
    curdir = Path.cwd()

    # create directory
    tmpdir = Path(curdir, "tmp_{}".format(int(time.time())))
    # tmpdir = Path(curdir, "tmp") #ATTN may need debug
    tmpdir.mkdir(exist_ok=True)

    # create field test subdirectories
    fieldTests = set([item["fieldTestName"] for item in queryMetadata])
    for fieldTestName in fieldTests:
        # create field test subdir
        testDir = Path(tmpdir, fieldTestName)
        testDir.mkdir(exist_ok=True)

        # dump metadata to ft folder
        ftLevelMetadata = [
            item for item in queryMetadata if item["fieldTestName"] == fieldTestName
        ]
        metadataFilename = fieldTestName + "_metadata.json"
        jsonFilepath = Path(testDir, metadataFilename)
        with open(jsonFilepath, "w") as outfile:
            json.dump(ftLevelMetadata, outfile)

    for item in queryMetadata:
        ftb_bucket.download_file(item["filename"], item["filename"])
        # put file in appropriate field test subdirectory
        Path(curdir, item["filename"]).rename(
            Path(tmpdir, item["fieldTestName"], item["filename"])
        )

    # store metadata in local json file
    jsonFilepath = Path(tmpdir, "metadata.json")
    with open(jsonFilepath, "w") as outfile:
        json.dump(queryMetadata, outfile)

    archiveName = tmpdir
    shutil.make_archive(archiveName, "zip", tmpdir)
    shutil.rmtree(tmpdir)

    return (str(tmpdir) + ".zip", queryMetadata)


"""=========== FRONT END DB =========================================================================="""

dbFE = "frontEndDB"
colFE = "metadataDefinition"


def metadataDefUpload(data: dict, userType):
    postUUID = str(uuid.uuid4())  # this will be the "_id" for the document
    unixUpload = int(time.time())
    data.update({"uploadTimestamp": unixUpload})
    data.update({"_id": postUUID})
    mongoMakePost(data, dbFE, colFE, userType)


def getMetadataDef(fieldTestType, userType):
    collection = accessMongoCollection(dbFE, colFE, userType)
    metadataDefinition = collection.find_one({"fieldTestType": fieldTestType})
    return metadataDefinition


def getFieldTestTypes(userType):
    collection = accessMongoCollection(dbFE, colFE, userType)
    fieldTestTypes = collection.distinct("fieldTestType")
    return fieldTestTypes


"""=========== USER DB =========================================================================="""


dbU = "userDB"
colU = "users"


def userDBUpload(data: dict, userType):
    postUUID = str(uuid.uuid4())  # this will be the "_id" for the document
    unixUpload = int(time.time())
    data.update({"uploadTimestamp": unixUpload})
    data.update({"_id": postUUID})
    mongoMakePost(data, dbU, colU, userType)


def getUser(un: str, userType):
    collection = accessMongoCollection("userDB", "users", userType)
    user = collection.find_one({"username": un})
    return user


def createUserDict(un, pw_hash, name, org, userType, email):
    return dict(
        userName=un,
        password=pw_hash,
        name=name,
        org=org,
        userType=userType,
        email=email,
    )


def updateUser(queryBy: str, key: str, updateField: str, updateVal: str, userType):
    collection = accessMongoCollection(dbU, colU, userType)
    mongoSuccess = collection.update_one(
        {queryBy: key}, {"$set": {updateField: updateVal}}
    )
    return mongoSuccess


def updateUserPW(un, pw_hash, userType):
    return updateUser(
        queryBy="username",
        key=un,
        updateField="password",
        updateVal=pw_hash,
        userType=userType,
    )
