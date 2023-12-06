from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk, ImageFile
from utils.packet import *
import time, socket, os, threading

ImageFile.LOAD_TRUNCATED_IMAGES = True

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

#CACHE_FILE_NAME = f"/cache-"
CACHE_FILE_EXT = ".jpg"

class Client():
    # Client connects to router through TCP
    def __init__(self, name, my_ip, a_router,tcp_p, udp_p, root):
        self.name = name
        self.my_ip = my_ip
        self.root = root
        self.createWidgets()
        self.client_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.client_TCP.connect((a_router, int(tcp_p)))
        self.client_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create UDP socket
        self.client_UDP.bind((my_ip, int(udp_p)))  # bind ip and address
        self.TIMEOUT = 5 # seconds to terminate connection
        self.responses = [] # updated(appended) in receive_flood_response.
                            # Each path WILL reach a Rendezvous point. 
        self.video_name = None
        self.CACHE_FILE_NAME = f"{self.name}/cache-"
        self.listen = True
        self.threads = []
    def createWidgets(self):
        """Build GUI."""
        # Create Setup button
        #self.setup = Button(self.master, width=20, padx=3, pady=3)
        #self.setup["text"] = "Setup"
        #self.setup["command"] = self.setupMovie
        #self.setup.grid(row=1, column=0, padx=2, pady=2)
        #
        ## Create Play button		
        #self.start = Button(self.master, width=20, padx=3, pady=3)
        #self.start["text"] = "Play"
        #self.start["command"] = self.playMovie
        #self.start.grid(row=1, column=1, padx=2, pady=2)
        #
        ## Create Pause button			
        #self.pause = Button(self.master, width=20, padx=3, pady=3)
        #self.pause["text"] = "Pause"
        #self.pause["command"] = self.pauseMovie
        #self.pause.grid(row=1, column=2, padx=2, pady=2)
        #
        # Create Teardown button
        self.teardown = Button(self.root, width=20, padx=3, pady=3)
        self.teardown["text"] = "Teardown"
        self.teardown["command"] =  self.exitClient
        self.teardown.grid(row=1, column=3, padx=2, pady=2)

        # Create a label to display the movie
        self.label = Label(self.root, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 

    def exitClient(self):
        """Teardown button handler."""
        packet = Packet(PacketType.SHUT_DOWN_REQUEST, (self.my_ip, self.video_name))
        CTT.send_msg(packet,self.client_TCP)
        print("A FECHAR....")
        time.sleep(1)
        #self.client_TCP.close()
        self.root.destroy() # Close the gui window
        os.remove(self.CACHE_FILE_NAME + str(self.name) + CACHE_FILE_EXT) # Delete the cache image from video
        self.listen = False
        for t in self.threads:
            t.join
        print("#"*10 +"END"+ "#"*10)

    def send_Flood_Req(self, video_name):
        print("Estou a enviar um FLOOD REQUEST ao server...")
        self.video_name = video_name
        packet = Packet(PacketType.FLOOD_REQUEST, [{}, False,(self.my_ip,video_name)])
        CTT.send_msg(packet,self.client_TCP)
    # N packets flood_response
    # sort p/ jumps
    # send_media_request
    
    # (flooding)    

    # router1_vizinhos -> flood req r22
    #                      flood req r3  
    
    #[r2] : movie.Mjpeg,
    #            [r2, r4, r5] : RP,
    #            [r3] : movie2.Mjpeg
    
    # router2 -> ...

    # se o filme que queres esta nos valores do dict entao pega nesse caminho
    # caso contratio manda para todos os vizinhos



    def send_Media_Req(self, video_name, flood_responses):
        #for caminho in target_info
        #try
        # translate the responses that were given by the router into the shortest paths
        # to reach a rendezvous point
        
        # path = sort_paths(self.responses)[0] <- temporary comment
        #print("Estou a enviar um MEDIA REQUEST ao server...")
        #path = ["10.0.2.10"]
        #packet = Packet(PacketType.MEDIA_REQUEST, (video_name, path))
        #CTT.send_msg(packet,self.client_TCP)
        nt = threading.Thread(target=self.recv_media)
        self.threads.append(nt)
        nt.start()
        #threading.Thread(target=self.recv_media).join()
       

    def recv_media(self) :
        start_time = time.time()
        frame_number = 0
        print("estou á espera de receber uma stream...")
        i = 1
        new_time = 0
        while self.listen:
            #print(i)
            packet,addr = CTT.recv_msg_udp(self.client_UDP)
            #print(msg, addr)
            if packet and packet.type == PacketType.MEDIA_RESPONSE:
                new_frame_number, frame = packet.data[0]
                print(f"tipo: {type(new_frame_number)}")
                print(f"data: {new_frame_number}")
                _,array = frame
                #print (packet.data[0], packet.data[1])
                if new_frame_number>frame_number:
                    frame_number = new_frame_number
                    self.updateMovie(self.writeFrame(array))
                    print("NEW FRAME RECIEVED")
                    new_time = time.time()
            elapsed_time = new_time - start_time
            start_time = new_time
            if elapsed_time > self.TIMEOUT:
                print("CONNECTION TIMEOUT")
                break
            i += 1

    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image = photo, height=288) 
        self.label.image = photo

    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = self.CACHE_FILE_NAME + self.name + CACHE_FILE_EXT
        #print(f"Frame length: {len(data)}")
        os.makedirs(os.path.dirname(cachename), exist_ok=True)
        file = open(cachename, "wb")
        file.write(data.tobytes())
        file.close()
        return cachename

    def recv_flood_response(self):
        while True:
            packet = CTT.recv_msg(self.client_TCP)
            if packet.type == PacketType.FLOOD_RESPONSE:
                print(packet)
                self.responses.append(packet)
            #print("das")
            #time.sleep(1)
    

    def send_Media_Shutdown(self, video_name, target_info):
        packet = Packet(PacketType.SHUT_DOWN_REQUEST, video_name)
        self.client_TCP.sendto(packet.encode())


def sort_paths(flood_responses):
    #filter flood responses by full paths and removes the auxiliar flag
    true_paths = [packet[0] for packet in flood_responses if packet[1]]
    #sorte the paths by len (number of jumps)
    true_paths =  sorted(true_paths, key=lambda x: len(x))
    return true_paths
