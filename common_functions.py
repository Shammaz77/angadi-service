from datetime import datetime, timedelta
import jwt
from flask import current_app, jsonify
from traceback import format_exc
from bson import ObjectId


def get_client_ip(request):

    '''
    Author: Muhammad Sidan
    Created on: 22 Nov 2024
    Purpose: To get the client IP address from the request headers
    '''

    x_forwarded_for = request.headers.get('X-Forwarded-For')

    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0].strip()
    else:
        client_ip = request.remote_addr

    return client_ip


def generate_token(user_obj):
    
    '''
    Created By : Surya kiran
    on: 18 Dec 2023
    To generate JWT token for a user
    '''

    try:

        token_payload = {
            'userObj': user_obj,
            'exp':  int((datetime.now() + timedelta(days=1)).strftime('%Y%m%d%H%M%S'))
        }

        token = jwt.encode(token_payload, current_app.config.get('JWT_SECRET_KEY'), algorithm="HS256")
        return token

    except Exception:
        error = format_exc()
        return jsonify({'message': 'INTERNAL SERVER ERROR', 'error': str(error)}), 500



def fn_convert_objects_to_string(data):

    """ Author: `Surya kiran`, Created on `21 Nov 2023`
    The following function will convert all objectids in passed
    argument to string

    Args:
        data: any
    
    Return:
        data: any
    """

    try:

        if isinstance(data, dict):
            for key in list(data):
                data[key] = fn_convert_objects_to_string(data[key])

        elif isinstance(data, list):
            index = 0
            for value in data:
                data[index] = fn_convert_objects_to_string(value)
                index += 1
        
        elif isinstance(data, ObjectId):
            data = str(data)
        
        elif isinstance(data, datetime):
            data = datetime.strftime(data, '%Y-%m-%d %H:%M:%S')

        return data

    except Exception:
        return None
    

