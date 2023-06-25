# USER DB TESTING BITCHEZ!!!
import cassutils.dbUtils.userDB as userDB

un = "mattMorrison"
pw = "iamstraight1"
name = "Matt Morrison"
email = "mcharlesmorrison@berkeley.edu"
org = "Cass Labs"
userType = "ftb_engineer_admin"

userDict = userDB.createUserDict(un, pw, name, org, userType, email)

userDB.userDBUpload(userDict, "ftb_engineer_admin")
