# USER DB TESTING BITCHEZ!!!
import ftb.db_utils as db_utils
import os 
# Existing passwords:
# mattMorrison pw=password
# axelJacobsen pw=iamgay1


# === get field names ===

# print(db_utils.get_unique_field_names("ftb_admin"))


# === query + download ===

#  exact match
# print(db_utils.exact_match_query("god_is_gay?\"", "yes?", "ftb_admin"))

# partial match
# print(db_utils.partial_match_query('god_is_gay?"', "yes", "ftb_admin"))

# download
# db_utils.download('god_is_gay?"', "yes", "ftb_admin")

# === delete field test data ===
"""example here:
query by "fieldTestType" so we get rid of all field tests of type "agoodone", then we
select the "frontEndDB" database and the "md_definition" collection, "ftb_admi"
is our user type
"""

# db_utils.delete_many("fieldTestType","agoodone","frontEndDB","md_definition","ftb_admin")


# === create new user ===

# un = "bigFatTool"
# pw = "iamgay1"
# name = "Zack Watkijns"
# email = "zackwatkins604@gmail.com"
# org = "Cass Labs"
# user_type = "ftb_admin"

# userDict = db_utils.create_user_dict(un, pw, name, org, user_type, email)
# db_utils.user_db_upload(userDict,"ftb_admin")


# # === update user passwords ===
# db_utils.update_user_pw("mattMorrison","password","ftb_admin")

# mattMorrison pw=password
# axelJacobsen pw=iamgay1


# UPLOADING SHITE

# projectName = "My Nigerian"
# fieldTestName = "Hello World 1"
# runName1 = "run 1"
# runName2 = "run 2"
# location = "Santa Cruz"
# trailNetwork = "Campus"
# trailName1 = "Dustys"
# trailName2 = "Silver Surfer"

# bikeID = "9098dad7-bf07-432c-93de-c46af6f3819c"
# bikeSetup = "NA"
# riderName = "Matt Morrison"
# riderHeight = 1.95
# riderWeight = 84
# # loggerID = "cl00"; fwVer = 0.00
# sensorIDs = ["pot200", "pot100", "reed_01", "button"]
# sensorPositions = ["A", "B", "C", "D"]
# notes = "NA"
# rotLogger = 0.9162979

# metadata1 = dict(
#     projectName=projectName,
#     fieldTestName=fieldTestName,
#     runName=runName1,
#     location=location,
#     trailNetwork=trailNetwork,
#     trailName=trailName1,
#     bikeID=bikeID,
#     bikeSetup=bikeSetup,
#     riderName=riderName,
#     riderHeight=riderHeight,
#     riderWeight=riderWeight,
#     sensorIDs=sensorIDs,
#     sensorPositions=sensorPositions,
#     notes=notes,
#     rotLogger=rotLogger,
# )
# metadata2 = dict(
#     projectName=projectName,
#     fieldTestName=fieldTestName,
#     runName=runName2,
#     location=location,
#     trailNetwork=trailNetwork,
#     trailName=trailName2,
#     bikeID=bikeID,
#     bikeSetup=bikeSetup,
#     riderName=riderName,
#     riderHeight=riderHeight,
#     riderWeight=riderWeight,
#     sensorIDs=sensorIDs,
#     sensorPositions=sensorPositions,
#     notes=notes,
#     rotLogger=rotLogger,
# )

""" FTB UPLOADING TO DB """
# post_data = [metadata1, metadata2]
# user_type = "ftb_admin"
# user_type = "ftb_field_tester"
# my_user = db_utils.get_user("mattMorrison", "ftb_engineer_admin")
# print(my_user["user_type"])

# filepath = "/Users/mattmorrison/Desktop/ftb/foxExports"
# db_utils.upload_many(filepath,post_data,user_type)


# === metadata definition ===

# md_def = dict(fieldTestType="agoodone", shit="shite!")
# db_utils.md_def_upload(md_def, "ftb_admin")
# print(db_utils.get_md_def("agoodone", "ftb_admin"))
# db_utils.delete_many(
#     "fieldTestType", "agoodone", "frontEndDB", "md_definition", "ftb_admin"
# )