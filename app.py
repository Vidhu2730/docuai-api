from flask import Flask, request, jsonify
from controller import handle_interaction
from confluence_interaction import confluence_bp
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(confluence_bp)

@app.route('/interact', methods=['POST'])
def interact():
    # Get data from the request
    data = request.json
    user_prompt = data.get("query")

    # Call the controller function
    response = handle_interaction(
        user_prompt
    )

    return response

@app.route('/confluence/search', methods=['GET'])
def search_confluence():
    search_term = request.args.get('query')
    if not search_term:
        return jsonify({"error": "Query parameter 'query' is required"}), 400
    search_url = f'https://docuaihackathonpoc.atlassian.net/wiki/rest/api/search'
    cql_query = f'text~"{search_term}"'
    params = {'cql': cql_query}
    response = requests.get(search_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN), params=params)
    print(response)
    if response.status_code == 200:
        results = response.json()
        return jsonify({"results": results})
    else:
        return jsonify({"error": "Failed to perform search", "status_code": response.status_code}), response.status_code

@app.route('/confluence/page/<page_id>', methods=['GET'])
def get_confluence_page(page_id):
    url = f'https://docuaihackathonpoc.atlassian.net/wiki/rest/api/content/{page_id}?expand=body.storage'
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
    if response.status_code == 200:
        data = response.json()
        body_storage_value = data['body']['storage']['value']
        # Remove HTML tags and get plain text
        soup = BeautifulSoup(body_storage_value, 'html.parser')
        plain_text = soup.get_text(separator="\n").strip()  # Get text without HTML tags
        
        return jsonify({"body_storage_value": plain_text})
    else:
        return jsonify({"error": "Failed to retrieve the page", "status_code": response.status_code}), response.status_code
    
if __name__ == '__main__':
    app.run(debug=True)