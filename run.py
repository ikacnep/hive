#!/usr/bin/env python3

import server.meat

server.meat.start(tls_cert='conf/fullchain.pem', tls_key='conf/privkey.pem', secret_key='conf/secret_key.txt')
