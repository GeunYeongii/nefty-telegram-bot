import requests

def assets(owner) :
    params = {
        "owner" : owner,
        "limit" : 5,
        "offset" : 0
    }
    return requests.get("https://testnets-api.opensea.io/api/v1/assets", params=params).json()

