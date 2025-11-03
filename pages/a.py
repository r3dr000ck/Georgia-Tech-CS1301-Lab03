import requests

url = "http://www.omdbapi.com/?apikey=89d15140&"
data = requests.get(url + "t=Inception").json()
print(data)