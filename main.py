from flask import Flask, jsonify, request
from traceback import format_exc
from bson import ObjectId
from datetime import datetime
from sellers import seller_setup
import os
from common_functions import get_client_ip, fn_convert_objects_to_string
from db import dbconn

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'JWT-ijk@3)*123456789ijhkdkhdgsta&*()$>/k12309545%fFsop')


@app.route('/addLocations', methods=['POST'])
def add_locations():

    try:

        data = request.get_json()

        if 'name' not in data:
            return jsonify({'statusCode': 400, 'message': 'Location Name not Found'})
        
        insert_obj = {
            'name': data['name'],
            'type': data['type'],
            'activeFlag': 1,
            'createdDate': datetime.now()
        }
        
        if data['type'] == 'location':

            insert_obj['stateId'] = ObjectId(data['stateId'])
            insert_obj['countryId'] = ObjectId(data['countryId'])
            insert_obj['districtId'] = ObjectId(data['districtId'])

        elif data['type'] == 'district':

            insert_obj['stateId'] = ObjectId(data['stateId'])
            insert_obj['countryId'] = ObjectId(data['countryId'])

        elif data['type'] == 'state':

            insert_obj['countryId'] = ObjectId(data['countryId'])

        dbconn.clnLocation.insert_one(insert_obj)

        return jsonify({'statusCode': 200, 'message': 'Location Inserted Succesfully'})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})
    

@app.route('/getLocation', methods=['GET'])
def get_locations():

    try:

        data = request.args

        query = {
            'type': data['type'],
            'activeFlag': 1
        }

        if data['type'] == 'location':

            if 'districtId' not in data:
                return jsonify({'statusCode': 400, 'message': 'districtId found'})
            
            query['districtId'] = ObjectId(data['districtId'])
            query['stateId'] = ObjectId(data['stateId'])

        elif data['type'] == 'district':

            if 'stateId' not in data:
                return jsonify({'statusCode': 400, 'message': 'StateId found'})
            query['stateId'] = ObjectId(data['stateId'])
            query['countryId'] = ObjectId(data['countryId'])

        elif data['type'] == 'state':

            if 'countryId' not in data:
                return jsonify({'statusCode': 400, 'message': 'countryId found'})
            
            query['countryId'] = ObjectId(data['countryId'])

        locations = list(dbconn.clnLocation.find(query, {'type':0,'createdDate':0,'activeFlag':0}))

        return jsonify({'statusCode': 200, 'message': 'Location Inserted Succesfully', 'locations': fn_convert_objects_to_string(locations)})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})


@app.route('/deleteLocation/<string:docId>', methods=['DELETE'])
def delete_location(docId):

    try:
        dbconn.clnLocation.update_one({'_id': ObjectId(docId)}, {'$set': {'activeFlag': 0, 'updatedDate': datetime.now()}})
        return jsonify({'statusCode': 200, 'message': 'location deleted Succesfully'})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})
    

@app.route('/addCategories', methods=['POST'])
def create_categories():

    try:

        data = request.get_json()

        if 'categoryName' not in data:
            return jsonify({'statusCode': 400, 'message': 'CategoryName found'})
        
        category = dbconn.clnCategory.find_one({'Name': data['categoryName']},{'_id':1})
        if category:
            return jsonify({'statusCode': 400, 'message': 'Category with this name already exists'})
        
        insert_obj = {
            'Name': data['categoryName'],
            'createdDate': datetime.now(),
            'activeFlag': 1
        }

        if 'logo' in data:
            insert_obj['logo'] = data['logo']

        dbconn.clnCategory.insert_one(insert_obj)

        return jsonify({'statusCode': 200, 'message': 'Category Inserted Succesfully'})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})
    
    
@app.route('/getCategories', methods=['GET'])
def fetch_categories():

    try:

        data = request.args

        query = {
            'activeFlag': 1
        }

        #find Cateogry with this query
        category_list = list(dbconn.clnCategory.find(query,{'createdDate':0,'activeFlag':0}))

        if 'countryId' in data:
            query['countryId'] = ObjectId(data['countryId'])

        if 'stateId' in data:
            query['stateId'] = ObjectId(data['stateId'])

        if 'districtId' in data:
            query['districtId'] = ObjectId(data['districtId'])

        if 'locationId' in data:
            query['locationId'] = ObjectId(data['locationId'])

        category_to_show = []
        for category in category_list:

            query['categoryId'] = category['_id']

            # findone atleast one shop in this category
            category_exists = dbconn.clnSellers.find_one(query, {'_id':1})
            if category_exists:
                category_to_show.append(category)

        return jsonify({'statusCode': 200, 'message': 'Fetched Categories', 'categories': fn_convert_objects_to_string(category_to_show)})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})
    
@app.route('/editCategory/<string:categoryId>', methods=['PATCH'])
def edit_category(categoryId):

    try:

        data = request.get_json()

        update_obj = {
            'updatedDate': datetime.now()
        }

        if 'categoryName' in data:
            update_obj['Name'] = data['categoryName']

        if 'logo' in data:
            update_obj['logo'] = data['logo']

        dbconn.clnCategory.update_one({'_id': ObjectId(categoryId)}, {'$set': update_obj})

        return jsonify({'statusCode': 200, 'message': 'category Updated Succesfully'})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})
    
@app.route('/deleteCategory/<string:categoryId>', methods=['DELETE'])
def delete_category(categoryId):

    try:
        dbconn.clnCategory.update_one({'_id': ObjectId(categoryId)}, {'$set': {'activeFlag': 0, 'updatedDate': datetime.now()}})
        return jsonify({'statusCode': 200, 'message': 'category deleted Succesfully'})
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})

@app.route('/createShopAndOffers', methods=['POST'])
def create_shop_and_offers():

    try:
        
        data = request.get_json()

        if 'categoryId' not in data:
            return jsonify({'statusCode': 400, 'message': 'categoryId found'})
        
        if 'Name' not in data:
            return jsonify({'statusCode': 400, 'message': 'Shop Name found'})
        
        if 'countryId' not in data:
            return jsonify({'statusCode': 400, 'message': 'countryId found'})
        
        if 'stateId' not in data:
            return jsonify({'statusCode': 400, 'message': 'stateId found'})

        if 'districtId' not in data:
            return jsonify({'statusCode': 400, 'message': 'districtId found'})

        
        insert_obj = {
            'activeFlag': 1,
            'Name': data['Name'],
            'categoryId': ObjectId(data['categoryId']),
            'categoryName': data['categoryName'],
            'cratedDate': datetime.now(),
            'countryId': ObjectId(data['countryId']),
            'stateId': ObjectId(data['stateId']),
            'districtId': ObjectId(data['districtId']),
        }

        if 'offerEndsIn' in data:
            insert_obj['offerEndsIn'] = datetime.strptime(data['offerEndsIn'], "%Y-%m-%dT%H:%M:%S")

        if 'locationId' in data:
            insert_obj['locationId'] = ObjectId(data['locationId'])

        if 'offers' in data:
            insert_obj['offers'] = data['offers']
        
        if 'logo' in data:
            insert_obj['logo'] = data['logo']

        dbconn.clnSellers.insert_one(insert_obj)

        return jsonify({'statusCode': 200, 'message': 'shop created Succesfully'})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})


@app.route('/deleteShop/<string:shopId>', methods=['DELETE'])
def delete_shop(shopId):

    try:

        # directly delete shop fron the db using shopId
        dbconn.clnSellers.update_one({'_id': ObjectId(shopId)}, {'$set': {'activeFlag': 0, 'updatedDate': datetime.now()}})
        return jsonify({'statusCode': 200, 'message': 'shop deleted Succesfully'})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})
    

@app.route('/editShops/<string:shopId>', methods=['PATCH'])
def edit_shop(shopId):

    try:

        data = request.get_json()

        update_obj = {
            'updatedDate': datetime.now()
        }

        if 'categoryId' in data:
            update_obj['categoryId'] = data['categoryId']
            update_obj['categoryName'] = data['categoryName']

        if 'Name' in data:
            update_obj['Name'] = data['Name']

        if 'countryId' in data:
            update_obj['countryId'] = data['countryId']

        if 'stateId' in data:
            update_obj['stateId'] = data['stateId']

        if 'districtId' in data:
            update_obj['districtId'] = data['districtId']

        if 'offerEndsIn' in data:
            update_obj['offerEndsIn'] = datetime.strptime(data['offerEndsIn'], "%Y-%m-%dT%H:%M:%S")

        if 'locationId' in data:
            update_obj['locationId'] = ObjectId(data['locationId'])

        if 'offers' in data:
            update_obj['offers'] = data['offers']

        if 'logo' in data:
            update_obj['logo'] = data['logo']

        dbconn.clnSellers.update_one({'_id': ObjectId(shopId)}, {'$set': update_obj})

        jsonify({'statusCode': 200, 'message': 'shop edited success'})

    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})
    
    
@app.route('/fetchShops', methods=['GET'])
def fetch_shops():

    try:

        data = request.args

        query = {
            'activeFlag': 1
        }

        if 'countryId' in data:
            query['countryId'] = ObjectId(data['countryId'])

        if 'stateId' in data:
            query['stateId'] = ObjectId(data['stateId'])

        if 'districtId' in data:
            query['districtId'] = ObjectId(data['districtId'])

        if 'locationId' in data:
            query['locationId'] = ObjectId(data['locationId'])

        if 'categoryId' in data:
            query['categoryId'] = ObjectId(data['categoryId'])

        sellers = list(dbconn.clnSellers.find(query,{'activeFlag':0,'offers':0}))

        return jsonify({'statusCode': 200, 'message': 'Shop fetched Succesfully', 'sellers': fn_convert_objects_to_string(sellers)})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})

@app.route('/fetchOffers/<string:shopId>', methods=['GET'])
def fetch_offers(shopId):

    try:

        # fetch shop detail using shopId
        offers = list(dbconn.clnSellers.find({'_id': ObjectId(shopId)}, {'activeFlag':0}))
        return jsonify({'statusCode': 200, 'message': 'offers fetched Succesfully', 'offers': fn_convert_objects_to_string(offers)})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})
    
@app.route('/registerasaseller', methods=['POST'])
def seller_account_registration():

    try:

        data = request.get_json()

        if 'userName' not in data:
            return jsonify({'statusCode': 400, 'message': 'username not found'})
        
        if 'password' not in data:
            return jsonify({'statusCode': 400, 'message': 'password not found'})

        if 'email' not in data:
            return jsonify({'statusCode': 400, 'message': 'email not found'})

        if 'fullName' not in data:
            return jsonify({'statusCode': 400, 'message': 'fullName not found'})
        
        client_ip = get_client_ip(request)
        user_agent = request.headers.get('User-Agent')
        req_origin = request.headers.get('Origin')
        
        insert_structure = {
            'profile': {
                'fullName': data['fullName'],
                'email': data['email'],
                'userName': data['userName']
            },
            'password': data['password'],
            'createdOn': datetime.now(),
            'activeFlag': 1,
            'createdAudit': {
                'IPAdress': client_ip,
                'deviceUSED': user_agent,
                'oRiGiN': req_origin
            },
            'roleObj': {
                'roleId': ObjectId(data['roleId']),
                'roleName': data['roleName']
            }
        }

        if 'mobile' in data:
            insert_structure['profile']['mobile'] = data['mobile']
        
        #create seller account

        return
    except Exception:
        return
    

app.register_blueprint(seller_setup, url_prefix='/seller')


if __name__ == '__main__': 
   app.run(debug = True)
