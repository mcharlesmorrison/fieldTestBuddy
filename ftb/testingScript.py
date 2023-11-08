# USER DB TESTING BITCHEZ!!!
import dbUtilities as dbUtils
import os 
# Existing passwords:
# mattMorrison pw=password
# axelJacobsen pw=iamgay1


# === get field names ===
# print(dbUtils.getUniqueFieldNames("ftb_admin"))

# === querying ===
#  THIS LOOKS FOR EXACT MATCHED
# print(dbUtils.ftbQuery("god_is_gay?\"", "yes?", "ftb_admin"))
# THIS LOOKS FOR PARTIAL MATCHES
# print(dbUtils.ftbPartialMatchQuery('god_is_gay?"', "yes", "ftb_admin"))
# dbUtils.ftbPartialMatchDownload('god_is_gay?"', "yes", "ftb_admin")
dbUtils.ftbQuery("fieldTestName", "1", "ftb_admin", os.curdir)
# === delete field test data ===
"""example here:
query by "fieldTestType" so we get rid of all field tsts of type "agoodone", then we
select the "frontEndDB" database and the "metadataDefinition" collection, "ftb_admi"
is our user type
"""
# dbUtils.deleteMany("fieldTestType","agoodone","frontEndDB","metadataDefinition","ftb_admin")


# === create new user ===
# un = "bigFatTool"
# pw = "iamgay1"
# name = "Zack Watkijns"
# email = "zackwatkins604@gmail.com"
# org = "Cass Labs"
# userType = "ftb_admin"

# userDict = dbUtils.createUserDict(un, pw, name, org, userType, email)
# dbUtils.userDBUpload(userDict,"ftb_admin")


# # === update user passwords ===
# dbUtils.updateUserPW("mattMorrison","password","ftb_admin")


un = "bigFatTool"
pw = "iamgay1"
name = "Zack Watkijns"
email = "zackwatkins604@gmail.com"
org = "Cass Labs"
userType = "ftb_admin"

# userDict = dbUtils.createUserDict(un, pw, name, org, userType, email)
# dbUtils.userDBUpload(userDict, "ftb_admin")
# mattMorrison pw=password
# axelJacobsen pw=iamgay1
# new pw: password
# dbUtils.updateUserPW("mattMorrison","password","ftb_admin")


# UPLOADING SHITE

projectName = "My Nigerian"
fieldTestName = "Hello World 1"
runName1 = "run 1"
runName2 = "run 2"
runName3 = "run 3"
runName4 = "run 4"
runName5 = "run 5"
runName6 = "run 6"
runName7 = "run 7"
location = "Santa Cruz"
trailNetwork = "Campus"
trailName1 = "Dustys"
trailName2 = "Silver Surfer"
trailName3 = "Grandpa"
trailName4 = "Wizard Sleeve"
trailName5 = "Jungle Drop"
trailName6 = "Jungle Drop"
trailName7 = "Chup"

bikeID = "9098dad7-bf07-432c-93de-c46af6f3819c"
bikeSetup = "NA"
riderName = "Matt Morrison"
riderHeight = 1.95
riderWeight = 84
# loggerID = "cl00"; fwVer = 0.00
sensorIDs = ["pot200", "pot100", "reed_01", "button"]
sensorPositions = ["A", "B", "C", "D"]
notes = "NA"
rotLogger = 0.9162979

metadata1 = dict(
    projectName=projectName,
    fieldTestName=fieldTestName,
    runName=runName1,
    location=location,
    trailNetwork=trailNetwork,
    trailName=trailName1,
    bikeID=bikeID,
    bikeSetup=bikeSetup,
    riderName=riderName,
    riderHeight=riderHeight,
    riderWeight=riderWeight,
    sensorIDs=sensorIDs,
    sensorPositions=sensorPositions,
    notes=notes,
    rotLogger=rotLogger,
)
metadata2 = dict(
    projectName=projectName,
    fieldTestName=fieldTestName,
    runName=runName2,
    location=location,
    trailNetwork=trailNetwork,
    trailName=trailName2,
    bikeID=bikeID,
    bikeSetup=bikeSetup,
    riderName=riderName,
    riderHeight=riderHeight,
    riderWeight=riderWeight,
    sensorIDs=sensorIDs,
    sensorPositions=sensorPositions,
    notes=notes,
    rotLogger=rotLogger,
)
metadata3 = dict(
    projectName=projectName,
    fieldTestName=fieldTestName,
    runName=runName3,
    location=location,
    trailNetwork=trailNetwork,
    trailName=trailName3,
    bikeID=bikeID,
    bikeSetup=bikeSetup,
    riderName=riderName,
    riderHeight=riderHeight,
    riderWeight=riderWeight,
    sensorIDs=sensorIDs,
    sensorPositions=sensorPositions,
    notes=notes,
    rotLogger=rotLogger,
)

""" FTB UPLOADING TO DB """
postData = [metadata1, metadata2, metadata3]
userType = "ftb_admin"
# userType = "ftb_field_tester"
# myUser = userDB.getUser("mattMorrison", "ftb_engineer_admin")
# print(myUser["userType"])
# userType = "casslabsadmin"

# filepath = "/Users/mattmorrison/Desktop/ftb/foxExports"
# ftbDB.ftbDbUploadBulk(filepath,postData,userType)

# fieldTestName = "Hello World 2"
# [tmpdir, fieldTestMetadata] = ftbDB.getftbFieldTest(fieldTestName, userType)
# print("my nigerian")
# print(dbUtils.deleteMany("fieldTestName","Hello World 1", "fieldTestDB", "fieldTestMD",userType))

# generic   query test
# bikeID = "9098dad7-bf07-432c-93de-c46af6f3819c"
# [tmpdir, queryMetadata] = ftbDB.ftbQuery("bikeID",bikeID,userType)
# print(tmpdir)


# metadataDef = dict(fieldTestType="agoodone", shit="shite!")
# dbUtils.metadataDefUpload(metadataDef, "ftb_admin")
# print(dbUtils.getMetadataDef("agoodone", "ftb_admin"))
# dbUtils.deleteMany(
#     "fieldTestType", "agoodone", "frontEndDB", "metadataDefinition", "ftb_admin"
# )