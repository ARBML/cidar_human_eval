
from database import read_responses

def fetch_and_display_responses():
    # Fetch responses from the database
    responses = read_responses()
    # Format the responses for display (simple text format in this example)
    formatted_responses = "\n".join([str(response) for response in responses])
    print(formatted_responses)
    # return formatted_responses

fetch_and_display_responses()