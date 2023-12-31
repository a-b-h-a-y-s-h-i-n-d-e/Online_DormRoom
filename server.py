import socket
import pickle
import threading

def broadcast(client_conn, clients, msg):
    try:
        for c in clients:
            if c != client_conn:
                c.send(msg)
                print(f'BROADCAST TO {c} SUCCESSFULLY!!')
            
            # this is called unnecessary things don't see this else condition!!
            # else:
            #     print(f'CLIENT NOT FOUND!')
                
                
    except Exception as e:
        print(f'ERROR IN BROADCASTING MESSAGES ! : {e}')
        # remove_client(client_conn)

def current_online_users_broadcast(clients, online_usernames):
    
    msg_dict = {
                'type' : 'online',
                'msg' : online_usernames
    }
    online_usernames_bytes = pickle.dumps(msg_dict)
    
    for c in clients:
        try:
            c.send(online_usernames_bytes)
            print(f'USERNAMES BROADCAST TO {c} SUCCESSFULLY!!')
        except Exception as e:
            print(f"ERROR IN SENDING ONLINE USERNAMES TO ALL CLIENTS -> {e}")
        except ConnectionAbortedError as e:
            break
    
    

def handle_client(client_conn, client_addr, clients, online_usernames):
    
    try:
        while True:
            
            # receiving messages from clients
            msg = client_conn.recv(2048)
            
            if not msg:
                break  # The client has disconnected
            
            msg_dis = pickle.loads(msg)
            print(msg_dis)
            username = msg_dis['name']
            
            # This is imp , because earlier the list was full of redundant usernames
            if username not in online_usernames:
                online_usernames.append(username)

            if len(clients) > 1:
                if msg_dis['type'] == 'joins':
                    current_online_users_broadcast(clients, online_usernames)
                broadcast(client_conn, clients, msg)

    except ConnectionAbortedError as e:
        print(f'CONNECTION ABORTED BY CLIENT: {client_addr[0]}: {e}')
        online_usernames.remove(username)
        remove_client(client_conn, clients, online_usernames)
        
    except ConnectionRefusedError as e:
        print(f'CONNECTION REFUSED BY CLIENT: {client_addr[0]}: {e}')
        online_usernames.remove(username)
        remove_client(client_conn, clients, online_usernames)
        
    except EOFError as e:
        print(f'CLIENT DISCONNECTED: {client_addr[0]}: {e}')
        online_usernames.remove(username)
        remove_client(client_conn, clients, online_usernames)
        
    # when client closes the window
    except ConnectionResetError as e:
        print(f'CLIENT LEAVED SO WE REMOVE IT :  {client_addr[0]} !! {client_addr[1]}')
        online_usernames.remove(username)
        remove_client(client_conn, clients, online_usernames)
        
    except Exception as e:
        print(f'UNKNOWN ERROR IN RECEIVING DATA: {client_addr[0]}: {e}')
        online_usernames.remove(username)
        remove_client(client_conn, clients, online_usernames)
    

def remove_client(client_conn, clients, online_usernames):
    if client_conn in clients:
        clients.remove(client_conn)
        print(f'Removed client {client_conn}')
    else:
        print(f' CLIENT WAS ALREADY REMOVED')
    
    if len(online_usernames) >= 1:
        current_online_users_broadcast(clients, online_usernames)

    
def run(server, clients, online_usernames):
    
    while True:
        try:
            client_conn, client_addr = server.accept()
            print(f'NEW CONNECTIONS FROM : {client_conn} : {client_addr[0]}')
            clients.append(client_conn)
            client_thread = threading.Thread(target= handle_client, args= (client_conn, client_addr, clients, online_usernames))
            client_thread.start()

        except ConnectionResetError as e:
            print(f'CLIENT HAS CLOSED THE CONNECTIONS SO REMOVING THE CLIENT {client_conn}')
            remove_client(client_conn, clients, online_usernames)
        except Exception as e:
            print(f'ERROR IN ACCEPTING CLIENTS : {e}')
            remove_client(client_conn, clients, online_usernames)
    

SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999
clients = []
online_usernames = []


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, SERVER_PORT))
server.listen()
print(f'SERVER HAS STARTED !!')
print(f'SERVER IS LISTENING ON {SERVER_IP} : {SERVER_PORT}')

run(server, clients, online_usernames)
