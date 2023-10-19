// Sample JSON object
const jsonObject = {
        "merchantId": "MERCHANTUAT",
        "merchantTransactionId": "MT7850590068188104",
        "merchantUserId": "MUID123",
        "amount": 10000,
        "redirectUrl": "https://webhook.site/redirect-url",
        "redirectMode": "REDIRECT",
        "callbackUrl": "https://webhook.site/callback-url",
        "mobileNumber": "9999999999",
        "paymentInstrument": {
          "type": "PAY_PAGE"
        }
};

// Convert the JSON object to a JSON string
const jsonString = JSON.stringify(jsonObject);

// Convert the JSON string to a Base64 string
const base64String = btoa(jsonString);

console.log(base64String);
