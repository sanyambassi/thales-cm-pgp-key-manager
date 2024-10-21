# thales-cm-pgp-key-manager 

# PGP Key Import/Export for CipherTrust

This is a web-based application that allows users to import and export PGP keys with a Thales CipherTrust Manager using a Web UI. It provides a simple interface to manage PGP keys on CipherTrust manager, and show results directly in the browser.

## Features

- Import PGP keys (either by pasting key contents or uploading a key file)
- Export PGP keys directly from the CipherTrust Manager
- Displays results in the browser
- Supports domains on CipherTrust Manager

## Prerequisites

To run this application, you will need:

- **Python 3.x**
- **Flask** for setting up the web server
- **OpenSSL** for generating the SSL certificates (or you can use your own)
- The following Python packages:
  - `flask`
  - `requests`

You can install the necessary dependencies by running:

```bash
pip install flask requests
```

## Application Setup

Clone the Repository: Clone this repository to your local machine:

```bash
git clone https://github.com/sanyambassi/thales-cm-pgp-key-manager.git
cd thales-cm-pgp-key-manager 
```

SSL Certificate Generation: This application uses SSL to ensure secure communication and generates a self-signed certificate when the application is launched. The certificate and private key are stored inside .\certs directory. You can also generate an SSL certificate manually to ensure secure communication. To generate a self-signed SSL certificate, run the following command:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/selfsigned.key -out certs/selfsigned.crt -subj "/CN=localhost"
```

## Run the Application 

Run the application using the following command:

```bash
python app.py
```

The application will be accessible at:

https://localhost:443

## Usage
- Importing a PGP Key
- Select the Import Key option.
- Enter the required details (CipherTrust Manager IP, username, password, domain, auth domain, and key name).
Paste the PGP key contents or upload a PGP key file.
Click Submit to import the PGP key.
Exporting a PGP Key
Select the Export Key option.
Enter the required details (CipherTrust Manager IP, username, password, domain, auth domain, and key name).
Click Submit to export the PGP key.
The exported PGP key will be displayed on the right side of the screen.

## Project Structure
bash
Copy code
pgp-key-import-export-ciphertrust/
│
├── app.py                      # Main Flask application file
├── certs/                       # Directory containing SSL certificates
│   ├── selfsigned.crt           # Self-signed certificate (generated)
│   └── selfsigned.key           # Self-signed private key (generated)
├── static/                      # Directory for static files (optional, if you add CSS or JavaScript)
├── templates/                   # Directory for HTML templates
│   └── index.html               # Main HTML template for the application
└── README.md                    # This readme file
