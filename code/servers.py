import json

if __name__=="__main__":
    with open("servers.json","r") as file:
        data = json.load(file)
        for router in data["routers"]:
            print(router["name"] + " neighbours => " + ", ".join(router["neighbours"]))
            

