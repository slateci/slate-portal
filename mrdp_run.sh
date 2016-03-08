export MRDP_DEBUG=True
export MRDP_APP_HOST=0.0.0.0
export MRDP_APP_PORT=4433
export MRDP_STATIC_ROOT=./static/
export MRDP_TEMPLATES_ROOT=views/
export MRDP_APP_SSL_CERT_PATH=./ssl/ssl_cert.pem
export MRDP_APP_SSL_KEY_PATH=./ssl/ssl_key.pem
python web_server.py
