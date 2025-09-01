# Generate CA
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
-subj "/C=CN/ST=OpenGauss/L=OpenGauss/O=MyOrg/OU=DB/CN=OpenGaussCA" \
-out ca.crt

# Generate server key / csr
openssl genrsa -out server.key 2048
openssl req -new -key server.key \
-subj "/C=CN/ST=OpenGauss/L=OpenGauss/O=MyOrg/OU=DB/CN=opengauss.local" \
-out server.csr

# SAN config (replace IP/DNS with the address you will use to access,
# e.g. 127.0.0.1 or host IP)
cat > san.cnf <<EOF
[ req ]
default_bits = 2048
distinguished_name = req_distinguished_name
req_extensions = req_ext
[ req_distinguished_name ]
[ req_ext ]
subjectAltName = @alt_names
[ alt_names ]
DNS.1 = opengauss.local
IP.1 = 127.0.0.1
EOF

# Sign server certificate with CA, include SAN
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
-out server.crt -days 730 -sha256 -extfile san.cnf -extensions req_ext

# Optional: client certificate (mutual TLS)
openssl genrsa -out client.key 2048
openssl req -new -key client.key -subj "/CN=dbclient" -out client.csr
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
-out client.crt -days 730 -sha256

