import os

def getcert():
  return {
  "type": "service_account",
  "project_id": os.environ.get('CERT-PROJECT-ID'),
  "private_key_id": os.environ.get('CERT-PRIVATE-KEY-ID'),
  "private_key": os.environ.get('CERT-PRIVATE-KEY').replace('\\n', '\n'),
  "client_email": os.environ.get('CERT-CLIENT-EMAIL'),
  "client_id": str(os.environ.get('CERT-CLIENT-ID')),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.environ.get('CERT-CLIENT-X509-CERT-URL')
}
