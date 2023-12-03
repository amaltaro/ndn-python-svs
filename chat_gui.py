import json
import os
import time
import tkinter as tk
import socket
import threading
import sys


HOST = "127.0.0.1"
JSON_FILE = sys.argv[1] + ".json"  # this corresponds to the node_id
NODE_NAME = sys.argv[1]  # contains the group_prefix
GROUP_NAME = sys.argv[2]  # contains the group_prefix
PORT = int(sys.argv[3])  # this is supposed to be the port number


def listen_for_messages():
    input_data = ""
    while True:
        if os.path.isfile(JSON_FILE) and os.access(JSON_FILE, os.R_OK):
            with open(JSON_FILE, "rt") as jo:
                data = json.load(jo)
            if input_data != data:
                root.after(0, lambda: display_message(data))
                input_data = data
        time.sleep(0.05)


def send_message():
    message = message_entry.get()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(message.encode('utf-8'))
    display_message(f"You: {message}")
    message_entry.delete(0, tk.END)


def display_message(message):
    chat_history.config(state=tk.NORMAL)
    chat_history.insert(tk.END, message + "\n")
    chat_history.config(state=tk.DISABLED)
    chat_history.yview(tk.END)

# Creating the main window
root = tk.Tk()
root.title("NDN SVS Chat application.")

# Creating some headers
group_header = tk.Message(root, text=f"Group prefix: {GROUP_NAME}", width=500)
group_header.config(bg='lightcyan4')
group_header.pack(padx=10, pady=10)
node_header = tk.Message(root, text=f"Node name: {NODE_NAME}", width=500)
node_header.config(bg='lightcyan4')
node_header.pack(padx=10, pady=10)

# Creating the chat history text box
chat_history = tk.Text(root, state=tk.DISABLED)
chat_history.pack(padx=10, pady=10)

# Creating the message entry field
message_entry = tk.Entry(root)
message_entry.pack(padx=10, pady=10, fill=tk.X)

# Creating the send button
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(padx=10, pady=10)

# Start listening for messages
threading.Thread(target=listen_for_messages, daemon=True).start()

root.mainloop()
