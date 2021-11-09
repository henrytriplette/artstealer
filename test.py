filename = id_generator(28)
print(filename);
url = "https://artbreeder.b-cdn.net/imgs/" + filename + ".jpeg"
response = requests.get(url)
if response.status_code == 200:
    with open("download/" + filename + ".jpg", 'wb') as f:
        f.write(response.content)
