from requests_html import HTMLSession

session = HTMLSession()

data_dictionary = {
    "name": "username",
    "password": "password123",
    "email": "user@example.com",
}

response = session.post("https://httpbin.org/post", data=data_dictionary)

print(response.text)
