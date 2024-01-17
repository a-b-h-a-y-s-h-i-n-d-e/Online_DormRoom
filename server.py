import socket
import pickle
import threading
import sys
import errno 
from database import Database

def broadcast(client_conn, clients, msg, online_usernames):
    try:
        for c,u in zip(clients,online_usernames):
            if c != client_conn:
                try:
                    c.send(msg)
                    print(f'BROADCAST TO {u} SUCCESSFULLY!!')
                except IOError as e:
                    if e.errno == errno.EPIPE:
                        remove_client(c, clients, online_usernames)
                        print("DANGLED SOCKET SPOTTED SO WE REMOVE THAT !!")
                except Exception as e:
                    raise


                
    except Exception as e:
        raise
        # print(f'ERROR IN BROADCASTING MESSAGES ! : {e}')
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
        
        except IOError as e:
            if e.errno == errno.EPIPE:
                remove_client(c, clients, online_usernames)
                print("DANGLED SOCKET SPOTTED SO WE REMOVE THAT !!")

            else:
                raise


        except EOFError as e:
            raise
            print("EOF error try again!")
        except Exception as e:
            raise
            # print(f"ERROR IN SENDING ONLINE USERNAMES TO ALL CLIENTS -> {e}")
        except ConnectionAbortedError as e:
            raise
            break

def remove_client(client_conn, clients, online_usernames):
    try:
        if client_conn in clients:
            print('before removing usernames -> ', online_usernames)
            
            # Get the index of the client_conn in the clients list
            index = clients.index(client_conn)
            
            # Remove the client_conn and its corresponding username
            clients.pop(index)
            removed_username = online_usernames.pop(index)
            
            print(f'Removed client {client_conn} with username {removed_username}')
            print('after removing usernames ->', online_usernames)
        else:
            print(f' CLIENT WAS ALREADY REMOVED')
        
        if len(online_usernames) >= 1:
            print("broadcasting these usernames -> ", online_usernames)
            current_online_users_broadcast(clients, online_usernames)
    except Exception as e:
        raise



def handle_client(client_conn, client_addr, clients, online_usernames, obj):
    
    try:
        while True:
            
            # receiving messages from clients
            msg = client_conn.recv(2048)
            
            if not msg:
                break  # The client has disconnected
            
            msg_dis = pickle.loads(msg)
            print(msg_dis)

            username = msg_dis['name']
            
            obj.insertData(msg_dis)

            # This is imp , because earlier the list was full of redundant usernames
            if username not in online_usernames:
                online_usernames.append(username)

            if msg_dis['type'] == 'joins':
                current_online_users_broadcast(clients, online_usernames)
                broadcast(client_conn, clients, msg, online_usernames)
            if msg_dis['type'] == 'left':
                print("----ONE CLIENT LEFT----")
                remove_client(client_conn, clients, online_usernames)
                broadcast(client_conn, clients, msg, online_usernames)

            if len(clients) > 1:
                broadcast(client_conn, clients, msg, online_usernames)

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
        print(e)
    
    
def run(server, clients, online_usernames):
    obj = Database()
    obj.connectToDB()
    obj.createTable()
    while True:
        try:
            client_conn, client_addr = server.accept()
            print(f'NEW CONNECTIONS FROM : {client_conn} : {client_addr[0]}')
            clients.append(client_conn)

            client_thread = threading.Thread(target= handle_client, args= (client_conn, client_addr, clients, online_usernames, obj))
            client_thread.start()
        except ConnectionResetError as e:
            print(f'CLIENT HAS CLOSED THE CONNECTIONS SO REMOVING THE CLIENT {client_conn}')
            remove_client(client_conn, clients, online_usernames)
        except Exception as e:
            print(e)
    

SERVER_IP = '127.0.0.1'
SERVER_PORT = 9996
clients = []
online_usernames = []


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, SERVER_PORT))
server.listen()
print(f'SERVER HAS STARTED !!')
print(f'SERVER IS LISTENING ON {SERVER_IP} : {SERVER_PORT}')



run(server, clients, online_usernames)

