from flask import Flask, jsonify, request
from traceback import format_exc
from bson import ObjectId
from datetime import datetime
from sellers import seller_setup
import os
from common_functions import get_client_ip, fn_convert_objects_to_string
from db import dbconn
from flask_cors import CORS

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'JWT-ijk@3)*123456789ijhkdkhdgsta&*()$>/k12309545%fFsop')

CORS(app, supports_credentials=True)

@app.route('/addLocations', methods=['POST'])
def add_locations():

    try:

        data = request.get_json()

        if 'name' not in data:
            return jsonify({'statusCode': 400, 'message': 'Location Name not Found'})
        
        if data['type'] == 'location':

            dbconn.clnLocation.update_one({'_id': ObjectId(data['countryId']), "states._id": ObjectId(data['stateId']), 'states.districts._id': ObjectId(data['districtId'])}, {'$push': {'states.$[state].districts.$[district].locations': {
                '_id': ObjectId(),
                'name': data['name'],
                'type': data['type'],
                'activeFlag': 1,
                'createdDate': datetime.now(),
            }}},array_filters=[
            {"state._id": ObjectId(data['stateId'])},
            {"district._id": ObjectId(data['districtId'])}
        ])   

        elif data['type'] == 'district':

            dbconn.clnLocation.update_one({'_id': ObjectId(data['countryId']), "states._id": ObjectId(data['stateId'])}, {'$push': {'states.$.districts': {
                '_id': ObjectId(),
                'name': data['name'],
                'type': data['type'],
                'activeFlag': 1,
                'createdDate': datetime.now(),
                'locations': []
            }}})    

        elif data['type'] == 'state':

            dbconn.clnLocation.update_one({'_id': ObjectId(data['countryId'])}, {'$push': {'states':{
                '_id': ObjectId(),
                'name': data['name'],
                'type': data['type'],
                'activeFlag': 1,
                'createdDate': datetime.now(),
                'districts': []
            }}})

        elif data['type'] == 'country':
            dbconn.clnLocation.insert_one({
                'name': data['name'],
                'type': data['type'],
                'activeFlag': 1,
                'createdDate': datetime.now(),
                'states': []
            })

        return jsonify({'statusCode': 200, 'message': 'Location Inserted Succesfully'})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode':500, 'message': 'Internal Server Error', 'error': str(error)})

@app.route('/getLocation', methods=['GET'])
def get_locations():

    try:
        locations = list(dbconn.clnLocation.find({'activeFlag':1},{'type':0,'createdDate':0,'activeFlag':0}))

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
            return jsonify({'statusCode': 400, 'message': 'CategoryName Not found'})
        
        category = dbconn.clnCategory.find_one({'Name': data['categoryName']},{'_id':1})
        if category:
            return jsonify({'statusCode': 400, 'message': 'Category with this name already exists'})
        
        insert_obj = {
            'Name': data['categoryName'],
            'createdDate': datetime.now(),
            'activeFlag': 1
        }

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
            return jsonify({'statusCode': 400, 'message': 'categoryId Not found'})
        
        if 'Name' not in data:
            return jsonify({'statusCode': 400, 'message': 'Shop Name Not found'})
        
        if 'countryId' not in data:
            return jsonify({'statusCode': 400, 'message': 'countryId Not found'})
        
        if 'stateId' not in data:
            return jsonify({'statusCode': 400, 'message': 'stateId Not found'})

        if 'districtId' not in data:
            return jsonify({'statusCode': 400, 'message': 'districtId Not found'})

        
        insert_obj = {
            'activeFlag': 1,
            'Name': data['Name'],
            'categoryId': ObjectId(data['categoryId']),
            'categoryName': data['categoryName'],
            'cratedDate': datetime.now(),
            'countryId': ObjectId(data['countryId']),
            'countryName': data['countryName'],
            'stateName': data['stateName'],
            'districtName': data['districtName'],
            'locationName': data['locationName'],
            'stateId': ObjectId(data['stateId']),
            'districtId': ObjectId(data['districtId']),
        }


        if 'locationId' in data:
            insert_obj['locationId'] = ObjectId(data['locationId'])

        if 'offers' in data:
            insert_obj['offers'] = []
            for offers in data['offers']:
                offer_obj = {
                    'poster': offers['image'],
                    'offerEndsIn': datetime.strptime(data['offerEndsIn'], "%Y-%m-%dT%H:%M:%S"),
                    'id': ObjectId()
                }
            insert_obj['offers'].append(offer_obj)
        
        if 'logo' in data:
            insert_obj['logo'] = data['logo']

        if 'Thumbnail' in data:
            insert_obj['Thumbnail'] = data['Thumbnail']

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
    

@app.route('/editShop/<string:shopId>', methods=['PATCH'])
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

        if 'locationId' in data:
            update_obj['locationId'] = ObjectId(data['locationId'])

        if 'offers' in data:
            for offers in data['offers']:
                if 'id' in offers:
                    result = dbconn.clnSellers.update_one(
                        {
                            '_id': ObjectId(shopId),
                            'offers.id': ObjectId(offers['id'])  # Match the existing offer in the array
                        },
                        {
                            '$set': {
                                'offers.$.poster': offers['poster'],
                                'offers.$.offerEndsIn': datetime.strptime(offers['offerEndsIn'], "%Y-%m-%dT%H:%M:%S")
                            }
                        }
                    )

                    if result.matched_count == 0:
                        # If no match, append the new offer
                        dbconn.clnSellers.update_one(
                            {'_id': ObjectId(shopId)},
                            {
                                '$push': {
                                    'offers': {
                                        'poster': offers['poster'],
                                        'offerEndsIn': datetime.strptime(offers['offerEndsIn'], "%Y-%m-%dT%H:%M:%S"),
                                        'id': ObjectId()  # Generate a new ObjectId for the offer
                                    }
                                }
                            }
                        )

                else:
                    # If no ID in the offer, treat it as a new offer
                    dbconn.clnSellers.update_one(
                        {'_id': ObjectId(shopId)},
                        {
                            '$push': {
                                'offers': {
                                    'poster': offers['poster'],
                                    'offerEndsIn': datetime.strptime(offers['offerEndsIn'], "%Y-%m-%dT%H:%M:%S"),
                                    'id': ObjectId()  # Generate a new ObjectId for the offer
                                }
                            }
                        }
                    )


        if 'logo' in data:
            update_obj['logo'] = data['logo']

        if 'Thumbnail' in data:
            update_obj['Thumbnail'] = data['Thumbnail']

        dbconn.clnSellers.update_one({'_id': ObjectId(shopId)}, {'$set': update_obj})

        return jsonify({'statusCode': 200, 'message': 'shop edited success'})

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

        return jsonify({'statusCode': 200, 'message': 'Shop fetched Succesfully', 'shops': fn_convert_objects_to_string(sellers)})
    
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
    
@app.route('/health-check', methods=['GET'])
def check_health():
    return jsonify({'status': True}), 200

@app.route('/fetchCategories', methods=['GET'])
def fetch_all_categories(): 

    try:

        category_list = list(dbconn.clnCategory.find({'activeFlag':1},{'activeFlag':0}))
        return jsonify({'statusCode': 200, 'categories': fn_convert_objects_to_string(category_list)})
    
    except Exception:
        error = format_exc()
        return jsonify({'statusCode': 200, 'categories': fn_convert_objects_to_string(category_list), 'error': str(error)})

    

app.register_blueprint(seller_setup, url_prefix='/seller')


if __name__ == '__main__': 
   app.run(debug = True)
