# USER DB TESTING BITCHEZ!!!
import dbUtilities as dbUtils

un = "bigFatTool"
pw = "iamgay1"
name = "Zack Watkijns"
email = "zackwatkins604@gmail.com"
org = "Cass Labs"
userType = "ftb_admin"

userDict = dbUtils.createUserDict(un, pw, name, org, userType, email)
dbUtils.userDBUpload(userDict,"ftb_admin")
# mattMorrison pw=password
# axelJacobsen pw=iamgay1
# new pw: password
# dbUtils.updateUserPW("mattMorrison","password","ftb_admin")

