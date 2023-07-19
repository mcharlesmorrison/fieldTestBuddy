# Back End Guide

Relevant notes for backend functions. Note: there is a "testingScript.py" file that can be used to test all these utility functions, and to clean up databases while we are uploading lots of shit that we'll want to delete.

## New/Relevant Functions

- `dbUtilities.ftbQuery(queryBy: str, searchString: str, userType)` downloads the field tests exactly matching the query. `queryBy` is a string denoting what field name you want to search by. `searchString` is the value we search for. **It must be an exact match**. 

- `dbUtilities.ftbPartialMatchQuery(queryBy: str, searchString: str, userType)` downloads the field tests partially matching the query. `queryBy` is a string denoting what field name you want to search by. `searchString` is the value we search for. **This will return all field tests that have a field value containing our search string for the field we are querying by**. I intend this function to be used by engineers when they query. We will generate a dropdown of things we can query by, and then also have a text box for them to filter their search. This function will take the user text input as the `searchString` argument.

- `dbUtilities.getUniqueFieldNames(userType)` returns a list of all unique field names in the field test metadata collection. This will be used for generating a list for the "search by" tab on the download page for engineers.

- `dbUtilities.deleteMany(queryBy: str, id: str, myDatabase: str, myCollection: str, userType)` deletes all documents in a mongo collection that have fields corresponding to "queryBy" that have values matching the "id" argument. If this is the field test collection, it will also delete all the corresponding S3 objects to keep things clean