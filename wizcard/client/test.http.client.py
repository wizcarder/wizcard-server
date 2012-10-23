import http.client
import json

# The URL should be pointing to the WhizCard webserver.
connection = http.client.HTTPSConnection('localhost')

# The transport between the iOS client and the WhizCard webserver is JSON.
headers = {'Content-type': 'application/json'}

# Build test JSON request.
request = {'user': 'anand'}
json_request = json.dumps(request)

# POST the request to specific path - this is not required if the request
# header could do the classification
connection.request('POST', '/register', json_request, headers)

# Dump the response arriving from the WhizCard webserver
response = connection.getresponse()
print(response.read().decode())
