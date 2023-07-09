# CSYE 6225 Fall '22

## How to run this app?

### Pre-requisites
* Python 3 installed on the machine
* Flask dependency installed
* Postman should be installed to test it locally

### Steps
1. Run the application from terminal using the command "python main.py".
2. To test it in the browser, just open the localhost (on port 5000) in the browser of choice.
3. To test the API using Postman, just copy the localhost URL and access it in Postman.

### Packer Commands
1. Format with: packer fmt {filename}
2. Validate with: packer validate {filename}
3. Build with: packer build {filename}

### Import SSL Certificate to AWS
aws acm import-certificate --profile=stage --certificate fileb://stage_utkarshneu.me/stage_utkarshneu_me.crt --certificate-chain fileb://stage_utkarshneu.me/stage_utkarshneu_me.ca-bundle --private-key fileb://stage_utkarshneu.me/private.key
