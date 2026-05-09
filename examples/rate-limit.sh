#!/usr/bin/env bash

for i in {1..20}; do
  curl -i -X POST http://127.0.0.1:8000/orders \
    -H "Content-Type: application/xml" \
    -H "X-API-Key: lab-demo-key" \
    --data-binary @valid-order.xml

done
