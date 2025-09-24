HTTP Methods for Each Endpoint:
1. Health Check
text
GET {{base_url}}/api/health
No headers needed

2. Single Analysis (Text)
text
POST {{base_url}}/api/detect
Headers: 
- X-API-Key: jackboys25
- Content-Type: application/json

Body (JSON):
{
    "text": "Your text here"
}
3. Single Analysis (File Upload)
text
POST {{base_url}}/api/detect
Headers:
- X-API-Key: jackboys25
- Content-Type: multipart/form-data

Body (form-data):
- Key: file, Type: File, Value: [Select your file]
4. Get History : GET
text
GET {{base_url}}/api/history
Headers:
- X-API-Key: jackboys25
5. Get Specific Analysis : GET
text
GET {{base_url}}/api/analysis/bb152374-b16b-4b8e-aa59-cf894eec36d1
Headers:
- X-API-Key: jackboys25
6. Get Session Info : GET
text
GET {{base_url}}/api/session
Headers:
- X-API-Key: jackboys25
7. Clear History : DELETE
text
DELETE {{base_url}}/api/clear-history
Headers:
- X-API-Key: jackboys25
Quick Reference Table:
Endpoint	Method	Purpose
/api/health	GET	Check server status
/api/detect	POST	Analyze text/file
/api/history	GET	Get analysis history
/api/analysis/{id}	GET	Get specific analysis
/api/session	GET	Get session info
/api/clear-history	DELETE	Clear history