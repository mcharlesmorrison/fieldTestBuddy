# USER DB TESTING BITCHEZ!!!
import dbUtilities as dbUtils

un = "mattMorrison"
pw = "iamstraight1"
name = "Matt Morrison"
email = "mcharlesmorrison@berkeley.edu"
org = "Cass Labs"
userType = "ftb_engineer_admin"

# userDict = userDB.createUserDict(un, pw, name, org, userType, email)

# new pw: password
dbUtils.updateUserPW("mattMorrison","password","ftb_admin")

