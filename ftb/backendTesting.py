import dbUtilities as dbUtils
# Existing passwords:
# mattMorrison pw=password
# axelJacobsen pw=iamgay1


# === get field names ===
print(dbUtils.getUniqueFieldNames("ftb_admin"))

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






