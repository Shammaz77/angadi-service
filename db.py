from pymongo import MongoClient
from os import getenv, environ

# environ['ATLAS_SRV'] = 'mongodb+srv://athultest:aTT66L87rsKSkh7p@cluster-angadiapp.92nvk.mongodb.net/'
environ['ATLAS_SRV'] = 'mongodb+srv://angadi:r2vME!-8HSSLhTd@cluster-angadiapp.92nvk.mongodb.net/'
environ['MONGO_DB'] = 'angadi_app'

ATLAS_CONNECTION_STRING = str(getenv('ATLAS_SRV'))
MONGO_DB = str(getenv('MONGO_DB'))

client = MongoClient(ATLAS_CONNECTION_STRING, ssl=True, tlsAllowInvalidCertificates=True)
dbconn = client[MONGO_DB]