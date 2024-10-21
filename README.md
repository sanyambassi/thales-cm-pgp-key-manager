# thales-cm-pgp-key-manager

# PGP Key Import/Export for CipherTrust

This is a web-based application that allows users to import and export PGP keys with a Thales CipherTrust Manager. It provides a simple interface to authenticate with the CipherTrust Manager, manage PGP keys (import/export), and show results directly in the browser.

## Features

- Import PGP keys (either by pasting key contents or uploading a key file)
- Export PGP keys directly from the CipherTrust Manager
- Display operation results in the browser
- Works with authentication that includes `domain` and `auth_domain` for CipherTrust Manager

## Prerequisites

To run this application, you will need:

- **Python 3.x**
- **Flask** for creating the web server
- **OpenSSL** for generating the SSL certificates (or you can use your own)
- The following Python packages:
  - `flask`
  - `requests`

You can install the necessary dependencies by running:

```bash
pip install flask requests
