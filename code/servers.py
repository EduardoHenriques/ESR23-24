import json

if __name__=="__main__":
    with open("servers.json","r") as file:
        data = json.load(file)
        for router in data["routers"]:
            print(router["name"] + " neighbours => " + ", ".join(router["neighbours"]))
            

# tipos de packet do cliente: start(a.k.a. flooding),request, shutdown
# arrancar cliente -> start -> (idle time) -> request -> (receber)flooding_response * N -> (enviar)request -> (receber)media_content -> ... -> shutdown 

# tipos de packet do router: flooding_request, flooding_response, media_request, media_content
# arrancar router -> listen -> (idle time)  -> (receber)flooding:_request -> (enviar)flooding_request * N 
#                                           -> (receber)flooding:_response * N -> (enviar)flooding_response * N
#                                           -> (receber)media_request * N ->  (enviar)media_request
#                                           -> ***(receber) media_content * N -> (enviar)media_content * N

# *** depende se os clientes estao a falar com o mesmo server ou nao

#tipos de packet do servidor: stream, flooding_response
# arrancar servidor -> listen -> (receber)flooding_request-> (enviar)flooding response -> stream -> stream...