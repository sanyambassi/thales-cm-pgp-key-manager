from flask import Flask, request, render_template, jsonify
import requests
import base64
import ssl
import os

app = Flask(__name__, static_folder='static')

# CipherTrust Manager authentication
def authenticate_to_ciphertrust(ip, username, password, domain, auth_domain):
    auth_url = f"https://{ip}/api/v1/auth/tokens/"
    auth_data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "domain": domain,
        "auth_domain": auth_domain
    }
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    response = requests.post(auth_url, json=auth_data, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()['jwt']
    return None

# Function to get the user ID
def get_user_id(ip, jwt):
    user_info_url = f"https://{ip}/api/v1/auth/self/user"
    headers = {
        'Authorization': f'Bearer {jwt}',
        'accept': 'application/json'
    }
    response = requests.get(user_info_url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()['user_id']
    return None

# Function to upload the PGP key
def upload_pgp_key(ip, jwt, key_name, key_material, user_id):
    upload_url = f"https://{ip}/api/v1/vault/secrets"
    headers = {
        'Authorization': f'Bearer {jwt}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    key_material_base64 = base64.b64encode(key_material.encode()).decode()
    secret_data = {
        "name": key_name,
        "dataType": "blob",
        "meta": {
            "ownerId": user_id
        },
        "material": key_material_base64
    }
    response = requests.post(upload_url, json=secret_data, headers=headers, verify=False)
    if response.status_code in [200, 201]:
        return True, response.json()
    return False, None

# Function to fetch the list of keys
def fetch_keys(ip, jwt):
    keys_url = f"https://{ip}/api/v1/vault/secrets?skip=0&limit=-1"
    headers = {
        'Authorization': f'Bearer {jwt}',
        'accept': 'application/json'
    }
    response = requests.get(keys_url, headers=headers, verify=False)

    try:
        response_data = response.json()
        if 'resources' in response_data:
            return response_data['resources']
        else:
            print(f"Unexpected response format: {response_data}")  # Log the unexpected format
            return None
    except Exception as e:
        print(f"Error parsing response: {e}, Response text: {response.text}")  # Log the parsing error
        return None

# Function to export the PGP key
def export_pgp_key(ip, jwt, key_name):
    export_url = f"https://{ip}/api/v1/vault/secrets/{key_name}/export"
    headers = {
        'Authorization': f'Bearer {jwt}',
        'accept': 'application/json'
    }
    response = requests.post(export_url, headers=headers, verify=False)
    if response.status_code == 200:
        key_material_base64 = response.json()['material']
        return base64.b64decode(key_material_base64).decode()
    return None

# Route for handling form submissions
@app.route('/process', methods=['POST'])
def process():
    data = request.form
    ip = data['ip']
    username = data['username']
    password = data['password']
    domain = data['domain']
    auth_domain = data['auth_domain']
    action = data['action']

    # Authenticate to CipherTrust Manager
    jwt = authenticate_to_ciphertrust(ip, username, password, domain, auth_domain)
    if not jwt:
        return jsonify({"error": "Authentication failed"})

    # Get the user ID
    user_id = get_user_id(ip, jwt)
    if not user_id:
        return jsonify({"error": "Failed to retrieve user ID"})

    # Handle single import
    if action == "import":
        key_name = data['key_name']
        key_contents = data.get('key_contents', None)

        if not key_contents and 'key_file' in request.files:
            key_file = request.files['key_file']
            key_contents = key_file.read().decode()

        if key_contents:
            success, response_data = upload_pgp_key(ip, jwt, key_name, key_contents, user_id)
            if success:
                return jsonify({"success": "Key successfully uploaded", "response": response_data})
            else:
                return jsonify({"error": "Failed to upload the key"})
        else:
            return jsonify({"error": "No key contents provided for import"})

    # Handle export
    elif action == "export":
        key_name = data.get('key_name')

        # If no key name is provided, fetch and return the list of keys
        if not key_name and 'selected_keys' not in data:
            keys = fetch_keys(ip, jwt)
            if keys:
                return jsonify({"keys": keys})
            else:
                return jsonify({"error": "Failed to fetch keys for export"})

        # If multiple keys are selected for export
        if 'selected_keys' in data:
            selected_keys = data.getlist('selected_keys')
            results = []
            for key in selected_keys:
                print(f"Attempting to export key: {key}")  # Log each key
                key_material = export_pgp_key(ip, jwt, key)
                if key_material:
                    results.append({"key_name": key, "key_material": key_material})
                else:
                    print(f"Failed to export key: {key}")  # Log failures
                    results.append({"key_name": key, "error": "Failed to export key"})
            return jsonify({"success": "Keys exported", "results": results})
    
        # If a single key name is provided for export
        if key_name:
            key_material = export_pgp_key(ip, jwt, key_name)
            if key_material:
                return jsonify({"success": "Key exported", "key_material": key_material})
            else:
                return jsonify({"error": "Failed to export key"})

    # Handle bulk import
    elif action == "bulk_import":
        if 'bulk_key_files' not in request.files:
            return jsonify({"error": "No key files uploaded for bulk import"})

        files = request.files.getlist('bulk_key_files')
        results = []

        for file in files:
            key_name = file.filename
            key_contents = file.read().decode()

            # Attempt to upload each key
            success, response_data = upload_pgp_key(ip, jwt, key_name, key_contents, user_id)
            if success:
                # Extract key ID and fingerprints from the response data
                key_id = response_data.get('id', 'Unknown ID')
                sha1_fingerprint = response_data.get('sha1Fingerprint', 'Unknown SHA1')
                sha256_fingerprint = response_data.get('sha256Fingerprint', 'Unknown SHA256')

                # Append detailed success report
                results.append({
                    "status": "success",
                    "key_name": key_name,
                    "key_id": key_id,
                    "sha1_fingerprint": sha1_fingerprint,
                    "sha256_fingerprint": sha256_fingerprint
                })
            else:
                # Append failure report
                results.append({
                    "status": "failure",
                    "key_name": key_name
                })

        return jsonify({"success": "Bulk import completed", "results": results})


# Function to generate a self-signed SSL certificate
def generate_self_signed_cert(cert_dir):
    cert_file = os.path.join(cert_dir, 'cert.crt')
    key_file = os.path.join(cert_dir, 'priv_key.pem')

    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        os.makedirs(cert_dir, exist_ok=True)
        # Create a self-signed certificate using OpenSSL via a subprocess
        os.system(f'openssl req -x509 -nodes -days 365 -newkey rsa:2048 '
                  f'-keyout {key_file} -out {cert_file} -subj "/CN=pgp-importer-exporter"')

    return cert_file, key_file

# Main route to serve the form
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Define a directory to store the generated certificates
    cert_directory = './certs'

    # Generate the self-signed certificate
    cert_file, key_file = generate_self_signed_cert(cert_directory)

    # Use SSL context to bind the certificate
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    # Run the app with SSL enabled on port 443
    app.run(host='0.0.0.0', port=443, ssl_context=context)