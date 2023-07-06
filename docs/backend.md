# Back End Guide

Relevant notes for backend functions. Note: there is a "backendTestin.py" file that can be used to test all these utility functions, and to clean up databases while we are uploading lots of shit that we'll want to delete.

## New/Relevant Functions

- `dbUtilities.getUniqueFieldNames(userType)` returns a list of all unique field names in the field test metadata collection. This will be used for generating a list for the "search by" tab on the download page for engineers.

- `dbUtilities.deleteMany(queryBy: str, id: str, myDatabase: str, myCollection: str, userType)` deletes all documents in a mongo collection that have fields corresponding to "queryBy" that have values matching the "id" argument. If this is the field test collection, it will also delete all the corresponding S3 objects to keep things clean