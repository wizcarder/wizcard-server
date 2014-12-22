openssl pkcs12 -clcerts -nokeys -out apns-dev-cert.pem -in apns-dev-cert.p12
openssl pkcs12 -nocerts -nodes -out apns-dev-key.pem -in apns-dev-key.p12
cat apns-dev-cert.pem apns-dev-key.pem > wizcard_ios_apns_dev.pem

openssl pkcs12 -clcerts -nokeys -out apns-prod-cert.pem -in apns-prod-cert.p12
openssl pkcs12 -nocerts -nodes -out apns-prod-key.pem -in apns-prod-key.p12
cat apns-prod-cert.pem apns-prod-key.pem > wizcard_ios_apns_production.pem
