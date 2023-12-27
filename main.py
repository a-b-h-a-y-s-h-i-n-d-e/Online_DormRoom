from tkinter import *
# from tkinter import ttk
from PIL import Image, ImageTk
import threading
import socket
import pickle



def login_page(client):
    global USERNAME

    def save_username():
        global USERNAME
        USERNAME = entry_text.get()
        print('username = ', USERNAME)
        window.destroy()
        chat_page(client, USERNAME)

    
        
    window = Tk()
    window.title('DormRoom')
    window.iconbitmap('images/logo.ico')
    screen_width = window.winfo_screenmmwidth()
    screen_height =  window.winfo_screenheight()
    window.geometry(f"650x450")
    window.resizable(FALSE, FALSE)
    
    bg_img = ImageTk.PhotoImage(Image.open('images/background.jpg').resize((650, 450)))
    
    frame = Frame(window, width=650, height=450)
    frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    bg_img_label = Label(frame, image=bg_img)
    bg_img_label.place(x=0, y=0)
    bg_img_label.update()
    
    username_label = Label(frame,text='Enter Username :',font=('Impact',20),bg="black",fg='#149414',width=15,height=1,)
    username_label.place(x=225, y=150)
    entry_text = StringVar()
    username_entry = Entry(frame, font=('Impact',15), bg='#FFFFFF', fg='#5F8575', width=18, textvariable=entry_text,justify=CENTER)
    username_entry.place(x=225, y=200)
    username_entry.bind('<Return>',lambda event: save_username())
    
    login_btn = Button(frame, text='LOGIN', height=1,width=13,command=save_username,  font=('Impact',14), bg='#149414', fg='#000000')
    login_btn.place(x=265, y=247)
    
    window.mainloop()



def chat_page(client, USERNAME):
    
    #useful functions
    def you_joins():
        
        msg_box.configure(state=NORMAL)
        msg = f"You" + " joins the chat!!\n"  
        msg_box.insert(END, msg, 'center bold')  # Apply the 'center' and 'bold' tags
        msg_box.tag_add("center", "1.0", "1.end")  # Limit the "center" tag to the first line
        msg_box.tag_configure("center", justify="center", foreground="black", background="orange", font=("Consolas", 15))
        msg_box.insert(END, '\n')
        msg_box.configure(state=DISABLED)
        

        msg_dict = {
            'type' : 'joins',
            'name' : USERNAME,
            'msg' : msg
        }
        msg_to_send = pickle.dumps(msg_dict)
        client.send(msg_to_send)
        
        
        
    
    def you_left():
        msg = USERNAME + 'left the chat!'
        msg_dict = {
            'type' : 'left',
            'name' : USERNAME,
            'msg' : msg
        }
        msg_to_send = pickle.dumps(msg_dict)
        client.send(msg_to_send)
        client.close()
        window.quit()
        window.destroy()
        
    def user_joins_chat_msg(username):
        
        msg_box.configure(state=NORMAL)
        msg = f"'{username}'" + " joins the chat!!\n"  
        msg_box.insert(END, msg, 'center bold')  # Apply the 'center' and 'bold' tags
        msg_box.tag_add("center", "1.0", "1.end")  # Limit the "center" tag to the first line
        msg_box.tag_configure("center", justify="center", foreground="black", background="orange", font=("Consolas", 15))
        msg_box.insert(END, '\n')
        msg_box.configure(state=DISABLED)
        
        # sending username to be displayed at online_box widget
        
        
    
    def user_left_chat_msg(username):
        
        msg_box.configure(state=NORMAL)
        msg = f"'{username}'" + " left the chat!!\n"  
        msg_box.insert(END, msg, 'center bold')  # Apply the 'center' and 'bold' tags
        msg_box.tag_add("center", "1.0", "1.end")  # Limit the "center" tag to the first line
        msg_box.tag_configure("center", justify="center", foreground="black", background="orange", font=("Consolas", 15))
        msg_box.insert(END, '\n')
        msg_box.configure(state=DISABLED)
    
        
    def display_msg(username, msg):
        
        dis_msg = f'{username} : {msg}'
        msg_box.configure(state=NORMAL)
        msg_box.tag_configure('left', justify='left', foreground='#581515', background='white',  font=('Helvetica Neue', 17), rmargin=15)
        msg_box.insert(END, dis_msg + '\n', 'left')
        msg_box.insert(END, '\n')
        msg_box.configure(state=DISABLED) 
        
        # to scroll down at the end
        msg_box.yview(END)        
    def send_message(event = None):
        msg = msg_entry.get()
        if msg != '':
            
            dis_msg = f'You : {msg}'
            msg_box.configure(state=NORMAL)
            msg_box.tag_configure('right', justify='right', foreground='white', font=('Helvetica Neue', 17), rmargin=15)
            msg_box.insert(END, dis_msg + '\n', 'right')
            msg_box.insert(END, '\n')
            msg_box.configure(state=DISABLED)
            
            msg_entry.delete(0, END)
            
        
            msg_dict = {
                'type' : 'msg',
                'name' : USERNAME,
                'msg' : msg
            }
            try:
                msg_to_sent = pickle.dumps(msg_dict)
            except Exception as e:
                print(f'ERROR IN SENDING DATA TO SERVER : {e} ')
            client.send(msg_to_sent)
            msg_dict = ''
            # clearing entry box!
    
    def recv_message():
        try:
            while True:
                obj = client.recv(2048)
                obj_dict = pickle.loads(obj)
                
                if obj_dict['type'] == 'joins':
                    user_joins_chat_msg(obj_dict['name'])
                
                if obj_dict['type'] == 'left':
                    user_left_chat_msg(obj_dict['name']) 

                if obj_dict['type'] == 'msg':
                    display_msg(obj_dict['name'], obj_dict['msg'])
                
                if obj_dict['type'] == 'online':
                    username_lists = obj_dict['msg']
                    print("The usernames list are = " + ', '.join(username_lists))
                    add_online_box(obj_dict['msg'])
                    
        except ConnectionAbortedError as e:
            print(f'CONNECTIONS CLOSED FROM SERVER !!')
            client.close()
            
        except Exception as e:
            print(f'ERROR IN RECIEVING MESSAGES : {e}')        
                                
                
    def add_online_box(usernames):
        print(usernames)
        # adding username to on_box widget
        on_box.config(state=NORMAL)
        on_box.delete("2.0", END)
        on_box.insert('2.0', '\n\nYou', 'body')
        
        for user in list(usernames):
            print(user)
            if user != USERNAME:
                on_box.insert('end', f"\n{user}", "body")
        on_box.config(state=DISABLED)   
        
        # scroll down at end
        on_box.yview(END)
        
    window = Tk()
    window.title('DormRoom')
    window.iconbitmap('images/logo.ico')
    window.geometry("650x450")
    window.resizable(FALSE, FALSE)
    
    # widgets declaration
    msg_box = Text(window, bg="#36454F",width=60,height=25,fg='white',state=DISABLED)
    msg_box.place(x=0,y=0)
    
    you_joins()
    
    msg_entry = Entry(window,bg="#FFFFFF",font=('Consolas',20),width=25)
    msg_entry.place(x=0,y=410)
    msg_entry.bind('<Return>', send_message)
    
    scrollbar = Scrollbar(window, orient= VERTICAL, bg= 'black', width=5)
    scrollbar.place(x= 485, y = 0)
    msg_box.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=msg_box.yview)
    
    send_btn = Button(window,text='SEND', height=1,width=12,  font=('Impact',13),
                      bg='#149414', fg='white', command= send_message)
    send_btn.place(x=380,y=409)
    
    on_box = Text(window,bg = "#8A9A5B",width = 13, height = 14, state = NORMAL, font=('Impact',17), fg='#F0FFFF')
    on_box.place(x=490, y=0)
    on_box.tag_configure('head', justify='center')
    on_box.tag_add('head', '1.0', '1.end')
    on_box.insert("1.0", 'Online\n\n', 'head')
    
    on_box.tag_configure('body', justify='center', foreground='#FFE4B5')
    on_box.tag_add('body', '2.0', '2.end')
    on_box.insert('2.0', '\nYou', 'body')
    on_box.config(state=DISABLED)
    
    
    
    quit_button =  Button(window,text='EXIT', height=1,width=14,  font=('Impact',17),
                      bg='red', fg='white', command=you_left)
    quit_button.place(x= 490, y= 400)
    
    
    recv_thread = threading.Thread(target=recv_message)
    recv_thread.start()
    
    # to tell window their is cross button 'X' to exit from window
    window.protocol("WM_DELETE_WINDOW", you_left)
    window.mainloop()




USERNAME = None
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((SERVER_IP, SERVER_PORT))
    
# added some exceptions
except ConnectionRefusedError:
    print(f"Connection to the server at {SERVER_IP}:{SERVER_PORT} was refused.")
except Exception as e:
    print(f'ERROR TO CONNECTING SERVER ! : {e}')



login_page(client)
#967969
#ECFFDC

#msg format{
 #      type  'joins' 'left' 'msg' 'online'
#       name
 #      msg
  #  
#}