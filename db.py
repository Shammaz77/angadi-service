from pymongo import MongoClient
from os import getenv

ATLAS_CONNECTION_STRING = str(getenv('ATLAS_SRV'))
MONGO_DB = str(getenv('MONGO_DB'))

client = MongoClient(ATLAS_CONNECTION_STRING, ssl=True, tlsAllowInvalidCertificates=True)
dbconn = client[MONGO_DB]