# Import necessary libraries and modules
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import hardwareDatabase as hardwareDB

'''
Structure of Project entry:
Project = {
    'projectName': projectName,
    'projectId': projectId,
    'description': description,
    'hwSets': {HW1: 0, HW2: 10, ...},
    'users': [user1, user2, ...]
}
'''
# Database and collection names
DB_NAME = 'HardwareCheckout'
COLLECTION = 'Projects'

# Helper function: gets the projects collection from client
def getCollection(client):
    return client[DB_NAME][COLLECTION]

# Helper function: check if number is an int
def isInt(value):
    return isinstance(value, int) and not isinstance(value, bool)

# Helper function: give units back to a hardware set using updateAvailability
# (it rejects anything that would push availability above capacity)
def returnUnits(client, hwSetName, qty):
    hw_set = hardwareDB.queryHardwareSet(client, hwSetName)
    if hw_set is None:
        return False
    return hardwareDB.updateAvailability(client, hwSetName, hw_set['availability'] + qty)

# Function to query a project by its ID
def queryProject(client, projectId):
    # Query and return a project from the database
    return getCollection(client).find_one({'projectId': projectId})

# Function to create a new project
def createProject(client, projectName, projectId, description):
    # Create a new project in the database
    # Check if the name or ID is invalid
    if not projectName or not projectId:
        return False

    projects = getCollection(client)

    # Unique index so two projects can't share an ID
    projects.create_index('projectId', unique=True)

    try:
        projects.insert_one({
            'projectName': projectName,
            'projectId': projectId,
            'description': description or '',
            'hwSets': {},
            'users': []
        })
    except DuplicateKeyError:
        return False
    return True

# Function to add a user to a project
def addUser(client, projectId, userId):
    # Add a user to the specified project
    if not userId:
        return False

    # $addToSet keeps the list free of duplicates
    result = getCollection(client).update_one(
        {'projectId': projectId},
        {'$addToSet': {'users': userId}}
    )
    return result.matched_count == 1

# Function to update hardware usage in a project
def updateUsage(client, projectId, hwSetName, delta):
    # Update the usage of a hardware set in the specified project
    # delta > 0 adds to the project's usage, delta < 0 removes from it
    if not hwSetName or not isInt(delta) or delta == 0:
        return False

    query = {'projectId': projectId}
    if delta < 0:
        # Usage may never drop below zero (can't check in more than was checked out)
        query[f'hwSets.{hwSetName}'] = {'$gte': -delta}

    result = getCollection(client).update_one(
        query,
        {'$inc': {f'hwSets.{hwSetName}': delta}}
    )
    return result.matched_count == 1

# Function to check out hardware for a project
def checkOutHW(client, projectId, hwSetName, qty, userId):
    # Check out hardware for the specified project and update availability
    if not isInt(qty) or qty <= 0 or not userId:
        return False
    if queryProject(client, projectId) is None:
        return False

    # Take the units from the hardware set (atomic, fails if not enough available)
    if not hardwareDB.requestSpace(client, hwSetName, qty):
        return False

    # Record the units against the project; hand them back if that fails
    if not updateUsage(client, projectId, hwSetName, qty):
        returnUnits(client, hwSetName, qty)
        return False
    return True

# Function to check in hardware for a project
def checkInHW(client, projectId, hwSetName, qty, userId):
    # Check in hardware for the specified project and update availability
    if not isInt(qty) or qty <= 0 or not userId:
        return False

    # Remove the units from the project first (fails if it has fewer checked out)
    if not updateUsage(client, projectId, hwSetName, -qty):
        return False

    # Return the units to the hardware set; undo the project change if that fails
    if not returnUnits(client, hwSetName, qty):
        updateUsage(client, projectId, hwSetName, qty)
        return False
    return True
