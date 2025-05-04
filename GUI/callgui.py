import tkinter as tk
import pygame.mixer
import subprocess
import threading
pygame.mixer.init()

# triggers event during call, which
# sends a message to another thread to open
# a window regarding the call!
def call_window(call_event,call_lock,call_id):
    # main window
    root = tk.Tk()
    root.geometry('300x400')
    root.title('📲 Calling App ☎️')
    root.rowconfigure(0,weight=1)
    root.rowconfigure(1,weight=4)
    root.columnconfigure(0,weight=1)
    

    # input fields...
    top_field = tk.Frame(root)
    top_field.grid(row=0,column=0,pady=10,sticky='nsew')

    input_field = tk.Text(top_field,height=1,font=("Arial",35))
    input_field.pack(padx=10,pady=10,fill='both')
    


    num_field = tk.Frame(root)
    num_field.grid(row=1,column=0,padx=10,pady=10,sticky='nsew')

    # creating buttons, with corresponding functions!
    dials_order = []
    for i in range(10):
        dials_order.append(pygame.mixer.Sound(f'GUI/Dialing/{i}Dial.mp3'))

    def insert_number(number):
        input_field.insert("end",number)
        dials_order[int(number)].play()
        

    def clear_input(inp):
        input_field.delete("1.0","end")

    def del_input(inp):
        # 1-char
        txt = input_field.get("1.0","end-1c")
        input_field.delete("1.0","end")
        input_field.insert("1.0",txt[:-1])

    # call should run in a seperate thread/trigger an event!
    def call(inp):
        num = input_field.get("1.0","end")
        print(f"Calling: {num}")

        # Lock?
        call_id[0] = num
        call_event.set()

        # do something to other thread/send info...

    # setting up buttons
    num_rows = 5
    num_cols = 3
    # getting given row and collumn w/ all buttons!
    bTest = tk.Button(root,text="None")
    dBgColor = bTest.cget("bg")
    dFgColor = bTest.cget("fg")
    buttons = [
        ('1',insert_number,dBgColor,dFgColor),('2',insert_number,dBgColor,dFgColor),('3',insert_number,dBgColor,dFgColor),
        ('4',insert_number,dBgColor,dFgColor),('5',insert_number,dBgColor,dFgColor),('6',insert_number,dBgColor,dFgColor),
        ('7',insert_number,dBgColor,dFgColor),('8',insert_number,dBgColor,dFgColor),('9',insert_number,dBgColor,dFgColor),
        ('Clr',clear_input,'red',dFgColor),('0',insert_number,dBgColor,dFgColor),('Del',del_input,'red',dFgColor),
        ('.',insert_number,dBgColor,dFgColor),('📞 ✅/❌',call,'blue','blue'),('+',insert_number,dBgColor,dFgColor)
    ]
    # setting all rows/cols equal
    for r in range(num_rows):
        num_field.rowconfigure(r,weight=1)
    for c in range(num_cols):
        num_field.columnconfigure(c,weight=1)


    en=0
    for (cmd,function,bgColor,fgColor) in buttons:
        button = tk.Button(num_field,text=cmd,font=("Arial",15),highlightbackground=bgColor,fg=fgColor)

        # need dynamicity
        button.config(command=lambda f=function, cmd=cmd: f(cmd))

        # expand fully
        button.grid(row=int(en/num_cols), column=en%num_cols,sticky='nsew',padx=3,pady=3)
        en += 1




    # showing window
    root.mainloop()


# for receiving a call
def recv_call(num):
    sound = pygame.mixer.Sound("GUI/Dialing/simpleringtone.mp3")
    sound.play()

    # display call
    appleScript = """
    tell application "System Events"
        display dialog "Incoming call" buttons {"Accept", "Decline"} default button "Accept" with icon 1 giving up after 30
    end tell
    """

    # running applescript
    r = subprocess.run(['osascript','-e',appleScript],capture_output=True,text=True)
    r.stdout

    if 'Accept' in (r.stdout):
        return True
    else: 
        return False

call_id = [None]
call_event = threading.Event()
call_lock = threading.Lock()
recv_call("23")
call_window(call_event,call_lock,call_id)