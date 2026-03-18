for i in {1..20}
do
  curl -X POST http://localhost:8000/orders \
    -H "Content-Type: application/xml" \
    -H "X-API-Key: test-key" \
    --data-binary @valid-order.xml
done