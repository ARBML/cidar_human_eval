from pymongo import MongoClient
import os 

password = os.environ.get('password')
uri = f"mongodb+srv://cidar:{password}@cluster0.yuhfxcj.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)
db = client['testDB']
collection = db['testCol']

def save_response(response_data):
    """Saves a response to the MongoDB collection."""

    try:
        # Insert the response data into the collection
        print("right before insertion")
        collection.insert_one(response_data)
        print("right after insertion")
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(0)

def read_responses(filter_query=None):
    """Reads responses from the MongoDB collection based on an optional filter."""
    try:
        if filter_query is None:
            filter_query = {}  # An empty query will return all documents
        responses = collection.find(filter_query)
        return list(responses)  # Convert cursor to list
    except Exception as e:
        print(f"An error occurred: {e}")
        return []