from flask import Flask, jsonify, request, Blueprint, make_response
from traceback import format_exc
from bson import ObjectId
from datetime import datetime
from common_functions import get_client_ip, generate_token

seller_setup = Blueprint('seller_setup', __name__)

@seller_setup.route('/login', methods=['POST'])
def seller_login():

    try:

        data = request.get_json()

        if 'userName' not in data:
            return jsonify({'statusCode': 400, 'message': 'UserName not found'})
        
        if 'password' not in data:
            return jsonify({'statusCode': 400, 'message': 'UserName not found'})
        
        client_ip = get_client_ip(request)
        user_agent = request.headers.get('User-Agent')
        req_origin = request.headers.get('Origin')

        # find user with username
        user = None
        if user is None:
            return jsonify({'statusCode': 403, 'message': 'UserName not found'})
        
        #find user with password
        if user is None:
            return jsonify({'statusCode': 403, 'message': 'Incorrect Password'})
        
        new_ip = True
        if 'IPAddress' in user:
            if client_ip in user['IPAddress']:
                new_ip = False
        
        if new_ip:
            # ipneed to insert
            #need to add session with sessionId, login_date, user_agent to an array of objects
            pass

        
        session_id = ObjectId()

        token_payload = {
            'userId': user['_id'],
            'roleId': user['roleId'],
            'sessionId': session_id
        }

        # need to insert session_id to logged session array and other audit_logs

        token_payload['profile'] = user['profile']

        token = generate_token(token_payload)
        response = make_response(jsonify({'active_user_data': user, 'access_token': token}))
        response.set_cookie('_csuid', str(user['_id']), httponly=True, secure=True, samesite='None')

        return response
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})

