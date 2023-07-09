from sqlite3 import Cursor
import pymysql
from app import app
from rds_config import mysql
from flask import request, jsonify
import bcrypt
import verify
import s3
import base64
from statsd import StatsClient
from flask_httpauth import HTTPBasicAuth

statsd = StatsClient(port=8125, prefix='CSYE6225-webapp')
auth = HTTPBasicAuth()

username = 'abc@xyz.edu'
password = 'helloneu'

s3_executor = s3.S3Executor()

@auth.verify_password
def authenticate(username, password):
    if username and password:
        if username == 'abc@xyz.edu' and password == 'helloneu':
            return True
        else:
            return False
    return False

#Error handling
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url, 
    }
    response = jsonify(message)
    response.status_code = 404
    return response

@app.errorhandler(400)
def bad_request(error=None):
    message = {
        'status': 400,
        'message': 'Bad Request',
    }
    response = jsonify(message)
    response.status_code = 400
    return response

@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
  
        statsd.incr('get_root')
        data = "hello world"
        return jsonify(data)

# Health check API which returns 200 OK is server call goes through
@app.route('/healthz', methods = ['GET'])
def healthz():
  
    statsd.incr('get_health_check')
    response = jsonify("Health is up!")
    response.status_code = 200
    return response

# Creating an account
@app.route('/v1/account', methods = ['POST'])
def create():

    statsd.incr('post_create_account')
    _json = request.json
    _firstName = _json['first_name']
    _lastName = _json['last_name']
    _password = _json['password']
    _username = _json['username']

    if _firstName and _lastName and _password and _username and request.method == 'POST':
        #encrypting the password using bCrypt salt
        salt = bcrypt.gensalt()
        _hashedPassword = bcrypt.hashpw(_password.encode('utf-8'), salt)
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_create_account_table = """CREATE TABLE IF NOT EXISTS account (
	                                    id bigint NOT NULL AUTO_INCREMENT,
                                        first_name VARCHAR(45),
                                        last_name VARCHAR(45),
                                        username VARCHAR(255),
                                        password VARCHAR(255),
                                        account_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                        account_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                        verified boolean default FALSE null,
                                        PRIMARY KEY (id)
                                    );"""
        cursor.execute(sql_create_account_table)
        sql = "INSERT INTO account(first_name, last_name, password, username) VALUES (%s, %s, %s, %s)"
        data = (_firstName, _lastName, _hashedPassword, _username)
        if(cursor.execute("SELECT * FROM account WHERE username=%s", _username)):
            return bad_request()
        cursor.execute(sql, data)
        conn.commit()
        cursor.execute("SELECT * FROM account WHERE username=%s", _username)
        response = jsonify()
        response.status_code
        if not verify.send_validation(email_address=_username):
            return "Bad request", 400
        return response, 201
    else:
        return not_found()

#Retrieving and updating an account with an accountId
@app.route('/v1/account/<int:id>', methods = ['GET'])
@auth.login_required
def get(id):
    #User Account retrieval
    statsd.incr('get_user_account_with_id')
    auth = get_authentication(request.headers)

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT account_created, account_updated, first_name, id, last_name, username FROM account WHERE id=%s", id)
    row = cursor.fetchone()
    response = jsonify(row)
    response.status_code
    return response

#Updating User Account
@app.route('/v1/account/<int:id>', methods=['GET', 'POST'])
@auth.login_required
def update(id):
    statsd.incr('update_user_account')
    _json = request.json
    _firstName = _json['first_name']
    _lastName = _json['last_name']
    _password = _json['password']

    if _firstName and _lastName and _password and request.method == 'POST':
        salt = bcrypt.gensalt()
        _hashedPassword = bcrypt.hashpw(_password.encode('utf-8'), salt)
        sql = "UPDATE account SET first_name=%s, last_name=%s, password=%s WHERE id=%s"
        data = (_firstName, _lastName, _hashedPassword, id)
        conn = mysql.connect()
        cursor = conn.cursor()
        if(cursor.execute("SELECT * FROM account WHERE id=%s", id)):
            cursor.execute(sql, data)
            conn.commit()
            response = jsonify('User updated successfully!')
            response.status_code
            return response
        else:
            return bad_request()
    else:
        return not_found()

#Retrieving List of all documents uploaded
@app.route('/v1/documents', methods=['GET'])
@auth.login_required
def getListOfDocuments():
    statsd.incr('get_all_documents')

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM document")
    rows = cursor.fetchall()
    response = jsonify(rows)
    response.status_code
    return response

#Uploading a document
@app.route('/v1/documents', methods=['POST'])
@auth.login_required
def createAndUploadDocument():
    statsd.incr('post_upload_document')
    _json = request.json
    _userId = _json['user_id']
    _name = _json['name']
    _s3BucketPath = _json['s3_bucket_path']

    if _userId and _name and _s3BucketPath and request.method == 'POST':
        sql = "INSERT INTO document(user_id, name, s3_bucket_path) VALUES(%s, %s, %s)"
        data = (_userId, _name, _s3BucketPath)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()

        response = jsonify("User added successfully.")
        response.status_code
        return response
    else:
        return not_found()

#Retrieve document by document identifier
@app.route('/v1/documents/<int:doc_id>', methods=['GET'])
@auth.login_required
def getByDocumentId(doc_id):
    statsd.incr('get_document_by_id')
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM documents WHERE doc_id=%s", doc_id)
    row = cursor.fetchone()
    response = jsonify(row)
    response.status_code
    return response

#Delete document by document identifier
@app.route('/v1/documents/<int:doc_id>', methods=['DELETE', 'GET'])
@auth.login_required
def deleteByDocumentId(doc_id):
    statsd.incr('delete_user_document')
    _json = request.json
    _userId = _json['user_id']
    _name = _json['name']
    _s3BucketPath = _json['s3_bucket_path']

    if _userId and _name and _s3BucketPath and request.method == 'DELETE':
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("DELETE FROM documents WHERE doc_id=%s", doc_id)
        row = cursor.fetchone()
        response = jsonify(row)
        response.status_code
        return response

@app.route('/v1/verify', methods=['GET'])
def verify_user():
    dic = request.args
    try:
        email = dic["email"]
        token = dic["token"]
        sql = "SELECT * FROM account where username=%s"
        data = email
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        if row:
            if verify.verify_token(email, token):
                vSql = "UPDATE account set verified=TRUE where username=%s"
                vData = email
                cursor.execute(vSql, vData)
                return "Your account has been successfully verified!", 200
            else:
                return "Your token is expired!", 200
        else:
            return "Bad Request", 400
    
    except KeyError or Exception:
        return "Bad request", 400

def get_authentication(req_header):
    if req_header.get('Authorization') is None:
        print("Not Authenticated!")
        return ""

    try:
        base64_auth = req_header['Authorization'].split("")[1]
        auth = base64.b64decode(base64_auth).decode('utf-8')
        return auth
    
    except Exception as e:
        print('Authentication error: %s' % e)
        return ""

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)