from flask import Flask, request
from flask import jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)

app.secret_key = "secretkey"
app.config['MONGO_URI'] = "mongodb://localhost:27017/exam-app"
mongo = PyMongo(app)


# def authenticate_user(username, password):
#     if username == "user" and password=="123":
#         return {"status" : True, "statusText" : "successfully logged in"}
#     else:
#         return {"status" : False, "statusText" : "invalid credencials"}


def create_user(username):
    print("User " + username + " created")
    return {"status" : True, "statusText" : "account created"}


def create_class():
    print("class names are added")
    return "success"


def add_pupil(pupil_name):
    print(pupil_name + " added")
    return "success"


def get_pupils(username, class_name):
    # fetch pupils by username and classname
    return [
        "Sam",
        "Tom",
        "Jhon",
        "Sean",
    ]


def get_paper_download_url(paper_id):
    return "http://www.africau.edu/images/default/sample.pdf"


def get_all_subjects():
    return [
        {
            "Category A": [
                {"Subcategory A-a": [
                    "test1"
                ]}
            ]
        },
        {
            "Category B": [
                {"Subcategory B-a": [
                    "test2"
                ]}
            ]
        }
    ]


def get_classes(final_classes_json):
    # fetch classes by username
    classNames = json.loads(final_classes_json)['class_names']
    return jsonify(classNames)
    # return [
    #     "Class 1",
    #     "Class 2",
    #     "Class 3",
    #     "Class 4",
    # ]


@app.route('/api/login', methods=['POST'])
def login():
    username = request.json['username'].encode('utf-8')
    password = request.json['password'].encode('utf-8')
    
    _hashed_password = generate_password_hash(password)
    login_user = mongo.db.teacher.find_one({'username': request.json['username'].encode('utf-8')})
    print("login_user")
    print(login_user)

    if login_user:
        if check_password_hash(_hashed_password,login_user["password"]):
            return jsonify({"status" : True, "statusText" : "successfully logged in"})

        else:
            return jsonify({"status" : False, "statusText" : "invalid credencials"})

    else:
        return jsonify({"status" : False, "statusText" : "invalid credencials"})        

    # return jsonify(authenticate_user(username, password))


@app.route('/api/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    # class_names = request.json['class_names']
    pupils = request.json['pupils']

    if username and password and email and pupils and request.method == 'POST':   
        existing_user = mongo.db.teacher.find_one({'username': request.json['username'].encode('utf-8')})
        print("existing_user")
        print(existing_user)
        print(type(existing_user))

        if existing_user is None:
            _hashed_password = generate_password_hash(password)
            id = mongo.db.teacher.insert({'username': username, 'password': _hashed_password, 'email': email, 'pupils': pupils})
            result = create_user(username)
            return jsonify(result)
            # message = {"status" : True, "statusText" : "account created"}
            # return jsonify(message)
        else:
            print("already have an account")  
            message = {"status" : False, "statusText" : "already have an account"}
            return jsonify(message)
            

@app.route('/api/deleteTeacher/<id>', methods=['delete'])
def deleteClass(id):
    mongo.db.teacher.delete_one({'_id': ObjectId(id)})
    result = jsonify("Teacher entry deleted successfully")
    return result

            
@app.route('/api/updateTeacher/<id>', methods=['PUT'])
def updateClass(id):
    _id = id 
    # username = request.json['username']
    # password = request.json['password']
    # email = request.json['email']
    class_names = request.json['class_names']
    # pupils = request.json['pupils']
    print(type(class_names))
    print("Json Class Name Array")
    print(class_names)

    # if username and password and email and class_name and pupils and _id and request.method == 'PUT': 
    if class_names and _id and request.method == 'PUT':  
        # _hashed_password = generate_password_hash(password)

        mongo.db.teacher.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
            {'$set': 
                # {'username': username, 'password': _hashed_password, 'email': email, 'class_names': class_names, 'pupils': pupils}
                {'class_names': class_names}
            }
        )
        result = create_class()
        return result
    else:
        print("Not Found")
        return not_found()



@app.route('/api/createClass', methods=['POST'])
def createClass():
    username = request.json['username']
    class_names = request.json['class_names']

    if class_names and username and request.method == 'POST':
        mongo.db.teacher.find_one_and_update({'username': username}, {'$set': { 'class_names': class_names}})
        result = create_class()
        return result

    else:
        print("Not Found")
        return not_found()

    


@app.route('/api/getClasses', methods=['POST'])
def getClasses():
    username = request.json['username']
    teacher_details = mongo.db.teacher.find({'username': username}, { 'class_names': 1, '_id': 0 })
    all_class_details = dumps(teacher_details)

    all_class_details_data = json.loads(all_class_details)
    final_classes_json = json.dumps(all_class_details_data[0])
    return get_classes(final_classes_json)   


@app.route('/api/getPupils', methods=['GET'])
def getPupils():
    username = request.args['username']
    class_names = request.args['class_names']
    return jsonify(get_pupils(username, class_names))


@app.route('/api/addPupil', methods=['POST'])
def addPupil():
    pupil_name = request.json['pupil_name']
    result = add_pupil(pupil_name)
    return jsonify(result)


# @app.route('/api/addTestPaper', methods=['POST'])
# def addTestPaper():
#     pupil_name = request.form['pupil_name']
#     result = add_pupil(pupil_name)
#     return result


@app.route('/api/getTestPaper', methods=['GET'])
def getTestPaper():
    paper_id = request.args['paper_id']
    return get_paper_download_url(paper_id)


@app.route('/api/getAllSubjects', methods=['GET'])
def getAllSubjects():
    return jsonify(get_all_subjects())

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found' + request.url 
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


if __name__ == "__main__":
    app.run(debug=True)