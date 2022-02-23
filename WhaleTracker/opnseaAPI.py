import requests

def assets() :
    owner = "0x000001f568875F378Bf6d170B790967FE429C81A"
    params = {
        "owner" : owner,
        "limit" : 5,
        "offset" : 0
    }
    return requests.get("https://testnets-api.opensea.io/api/v1/assets", params=params).json()

