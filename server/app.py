# Import necessary libraries and modules
import os
from bson.objectid import ObjectId
from flask import Flask, request, jsonify
from pymongo import MongoClient

# Import custom modules for database interactions
import usersDatabase as usersDB
import projectsDatabase as projectsDB
import hardwareDatabase as hardwareDB
from encryption import protect_user_id

# MongoDB connection string, read from the environment so credentials stay out of git
# (falls back to a local MongoDB for development)
from dotenv import load_dotenv
load_dotenv()

MONGODB_SERVER = os.environ.get("MONGODB_SERVER", "mongodb://localhost:27017")

# Enables secure SSL verification for MongoDB connections
MONGODB_CA_FILE = os.environ.get("SSL_CERT_FILE")

# Demo mode: set USE_MOCK_DB=1 to use an in-memory fake MongoDB (no database needed).
# All routes share one client so data persists between requests; close() is a no-op.
if os.environ.get("USE_MOCK_DB"):
    import mongomock
    _mock_client = mongomock.MongoClient()
    _mock_client.close = lambda: None

    def MongoClient(*args, **kwargs):
        return _mock_client

# One shared client for the whole app. MongoClient keeps a pool of open connections,
client = MongoClient(MONGODB_SERVER, tlsCAFile=MONGODB_CA_FILE)

# Initialize a new Flask web application
app = Flask(__name__)

# Helper function, checks if MongoDB document contains ObjectId in '_id'
def clean_doc(doc):
    if doc is None:
        return None
    doc = dict(doc)
    if isinstance(doc.get('_id'), ObjectId):
        doc['_id'] = str(doc['_id'])
    return doc

# Helper function, cleans project documents and adds the owner's display name
def with_owner_names(projects):
    names = usersDB.getUsernames(client, {projectsDB.getOwner(p) for p in projects})
    return [dict(clean_doc(p), ownerName=names.get(projectsDB.getOwner(p))) for p in projects]

# Helper function, parse a positive number from request data
def parse_qty(value):
    try:
        qty = int(value)
    except (TypeError, ValueError):
        return None
    return qty if qty > 0 else None

DEFAULT_HW_SETS = {'HWSet1': 100, 'HWSet2': 100}

def seed_hardware_sets():
    try:
        for hwSetName, capacity in DEFAULT_HW_SETS.items():
            # does nothing if the set already exists, so availability isn't reset on restart
            hardwareDB.createHardwareSet(client, hwSetName, capacity)
    except Exception as e:
        print(f'Could not seed hardware sets: {e}')

# runs on import so it works under gunicorn too; tests can set SKIP_SEED=1
if not os.environ.get('SKIP_SEED'):
    seed_hardware_sets()

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    # Get specific data
    userId = data.get('userId')
    password = data.get('password')

    # Check for errors
    if not userId or not password:
        return jsonify({'success': False,'message': 'userId and password are required'}), 400

    # Hash the userId so it matches what's stored
    hashedId = protect_user_id(userId)

    try:
        # Attempt to log in the user using the usersDB module
        success = usersDB.login(client, hashedId, password)
    # Catch error
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500

    # Return a JSON response
    if success:
        return jsonify({'success': True, 'message': 'Login successful', 'userId': userId}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Route for the main page (Work in progress)
@app.route('/main')
def mainPage():
    # Extract data from request (GET, so it comes from the query string: /main?userId=jb123)
    userId = request.args.get('userId')

    if not userId:
        return jsonify({'success': False, 'message': 'userId is required'}), 400

    hashedId = protect_user_id(userId)
    try:
        # Fetch user projects using the usersDB module
        projects = usersDB.getUserProjectsList(client, hashedId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500

    # Return a JSON response
    if projects is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'userId': userId, 'projects': projects}), 200

# Route for joining a project
@app.route('/join_project', methods=['POST'])
def join_project():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    userId = data.get('userId')
    projectId = data.get('projectId')

    if not userId or not projectId:
        return jsonify({'success': False,
                        'message': 'userId and projectId are required'}), 400

    hashedId = protect_user_id(userId)
    try:
        # Attempt to join the project using the usersDB module
        success = usersDB.joinProject(client, hashedId, projectId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500

    # Return a JSON response
    if success:
        return jsonify({'success': True,
                        'message': f'Joined project {projectId}'}), 200
    return jsonify({'success': False,
                    'message': 'Could not join project (check that the project ID exists)'}), 400

# Route for adding a new user
@app.route('/add_user', methods=['POST'])
def add_user():
     # Extract data from request
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    userId = data.get('userId')
    password = data.get('password')

    if not username or not userId or not password:
        return jsonify({'success': False,
                        'message': 'username, userId, and password are required'}), 400

    hashedId = protect_user_id(userId)
    try:
        # Attempt to add the user using the usersDB module
        success = usersDB.addUser(client, username, hashedId, password)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500

    # Return a JSON response
    if success:
        return jsonify({'success': True, 'message': 'Account created',
                        'username': username, 'userId': userId}), 201
    return jsonify({'success': False, 'message': 'That userId is already taken'}), 409

# Route for getting the list of user projects
@app.route('/get_user_projects_list', methods=['POST'])
def get_user_projects_list():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    userId = data.get('userId')
 
    if not userId:
        return jsonify({'success': False, 'message': 'userId is required'}), 400

    hashedId = protect_user_id(userId)
    try:
        # Fetch the user's projects using the usersDB module
        projects = usersDB.getUserProjectsList(client, hashedId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
 
    # Return a JSON response
    if projects is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'projects': projects}), 200

# Route for getting the user's projects with details, split into owned and shared
@app.route('/get_user_projects', methods=['POST'])
def get_user_projects():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    userId = data.get('userId')

    if not userId:
        return jsonify({'success': False, 'message': 'userId is required'}), 400

    hashedId = protect_user_id(userId)
    try:
        # Fetch the user's project IDs, then all of those projects in one query
        projectIds = usersDB.getUserProjectsList(client, hashedId)
        if projectIds is None:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        projects = with_owner_names(projectsDB.queryProjects(client, projectIds))
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500

    # Return a JSON response
    owned = [p for p in projects if projectsDB.getOwner(p) == hashedId]
    shared = [p for p in projects if projectsDB.getOwner(p) != hashedId]
    return jsonify({'success': True, 'owned': owned, 'shared': shared}), 200

# Route for creating a new project
@app.route('/create_project', methods=['POST'])
def create_project():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    projectName = data.get('projectName')
    projectId = data.get('projectId')
    description = data.get('description', '')
    userId = data.get('userId')  # optional: the creator owns and is added to the project

    if not projectName or not projectId:
        return jsonify({'success': False,
                        'message': 'projectName and projectId are required'}), 400

    owner = protect_user_id(userId) if userId else None
    try:
        # Attempt to create the project using the projectsDB module
        success = projectsDB.createProject(client, projectName, projectId, description, owner)

        # If created and we know who made it, add the creator as a member
        if success and owner:
            usersDB.joinProject(client, owner, projectId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
 
    # Return a JSON response
    if success:
        return jsonify({'success': True, 'message': 'Project created',
                        'projectId': projectId}), 201
    return jsonify({'success': False, 'message': 'That projectId is already taken'}), 409

# Route for getting project information
@app.route('/get_project_info', methods=['POST'])
def get_project_info():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    projectId = data.get('projectId')
 
    if not projectId:
        return jsonify({'success': False, 'message': 'projectId is required'}), 400
 
    try:
        # Fetch project information using the projectsDB module
        project = projectsDB.queryProject(client, projectId)
        if project is not None:
            project = with_owner_names([project])[0]
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500

    # Return a JSON response
    if project is None:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    return jsonify({'success': True, 'project': project}), 200

# Route for getting all hardware names
@app.route('/get_all_hw_names', methods=['POST'])
def get_all_hw_names():
    try:
        # Fetch all hardware names using the hardwareDB module
        hw_names = hardwareDB.getAllHwNames(client)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
 
    # Return a JSON response
    return jsonify({'success': True, 'hwNames': hw_names or []}), 200

# Route for getting hardware information
@app.route('/get_hw_info', methods=['POST'])
def get_hw_info():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    hwSetName = data.get('hwSetName')
 
    if not hwSetName:
        return jsonify({'success': False, 'message': 'hwSetName is required'}), 400
 
    try:
        # Fetch hardware set information using the hardwareDB module
        hw_set = hardwareDB.queryHardwareSet(client, hwSetName)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
 
    # Return a JSON response
    if hw_set is None:
        return jsonify({'success': False, 'message': 'Hardware set not found'}), 404
    return jsonify({'success': True,
                    'hwName': hw_set.get('hwName'),
                    'capacity': hw_set.get('capacity'),
                    'availability': hw_set.get('availability')}), 200

# Route for checking out hardware
@app.route('/check_out', methods=['POST'])
def check_out():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    projectId = data.get('projectId')
    hwSetName = data.get('hwSetName')
    userId = data.get('userId')
    qty = parse_qty(data.get('qty'))
 
    if not projectId or not hwSetName or not userId:
        return jsonify({'success': False,
                        'message': 'projectId, hwSetName, and userId are required'}), 400
    if qty is None:
        return jsonify({'success': False,
                        'message': 'qty must be a positive whole number'}), 400
 
    try:
        # Attempt to check out the hardware using the projectsDB module
        success = projectsDB.checkOutHW(client, projectId, hwSetName, qty, protect_user_id(userId))
 
        # Grab the updated availability so the UI can refresh immediately
        hw_set = hardwareDB.queryHardwareSet(client, hwSetName)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
 
    availability = hw_set.get('availability') if hw_set else None
 
    # Return a JSON response
    if success:
        return jsonify({'success': True,
                        'message': f'Checked out {qty} unit(s) of {hwSetName}',
                        'availability': availability}), 200
    return jsonify({'success': False,
                    'message': f'Request exceeds available units of {hwSetName}',
                    'availability': availability}), 400

# Route for checking in hardware
@app.route('/check_in', methods=['POST'])
def check_in():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    projectId = data.get('projectId')
    hwSetName = data.get('hwSetName')
    userId = data.get('userId')
    qty = parse_qty(data.get('qty'))
 
    if not projectId or not hwSetName or not userId:
        return jsonify({'success': False,
                        'message': 'projectId, hwSetName, and userId are required'}), 400
    if qty is None:
        return jsonify({'success': False,
                        'message': 'qty must be a positive whole number'}), 400
 
    try:
        # Attempt to check in the hardware using the projectsDB module
        success = projectsDB.checkInHW(client, projectId, hwSetName, qty, protect_user_id(userId))
 
        # Grab the updated availability so the UI can refresh immediately
        hw_set = hardwareDB.queryHardwareSet(client, hwSetName)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
 
    availability = hw_set.get('availability') if hw_set else None
 
    # Return a JSON response
    if success:
        return jsonify({'success': True,
                        'message': f'Checked in {qty} unit(s) of {hwSetName}',
                        'availability': availability}), 200
    return jsonify({'success': False,
                    'message': 'Cannot check in more units than the project has checked out',
                    'availability': availability}), 400

# Route for creating a new hardware set
@app.route('/create_hardware_set', methods=['POST'])
def create_hardware_set():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    hwSetName = data.get('hwSetName')
    initCapacity = parse_qty(data.get('initCapacity'))
 
    if not hwSetName:
        return jsonify({'success': False, 'message': 'hwSetName is required'}), 400
    if initCapacity is None:
        return jsonify({'success': False,
                        'message': 'initCapacity must be a positive whole number'}), 400
 
    try:
        # Attempt to create the hardware set using the hardwareDB module
        success = hardwareDB.createHardwareSet(client, hwSetName, initCapacity)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
 
    # Return a JSON response
    if success:
        return jsonify({'success': True,
                        'message': f'Hardware set {hwSetName} created',
                        'capacity': initCapacity}), 201
    return jsonify({'success': False,
                    'message': 'A hardware set with that name already exists'}), 409

# Route for checking the inventory of projects
@app.route('/api/inventory', methods=['GET'])
def check_inventory():
    try:
        # Fetch all projects
        projects = [clean_doc(p) for p in client['HardwareCheckout']['Projects'].find({})]
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
 
    # Return a JSON response
    return jsonify({'success': True, 'projects': projects}), 200

# Main entry point for the application
if __name__ == '__main__':
    app.run()
