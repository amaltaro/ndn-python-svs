import tkinter as tk
import socket
import threading
import sys


HOST = "127.0.0.1"
PORT = int(sys.argv[1])  # this is supposed to be the port number


def listen_for_messages():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.connect((HOST, PORT))
        while True:
            message = server_socket.recv(1024).decode('utf-8')
            if message:
                root.after(0, lambda: display_message(f"Other: {message}"))


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
root.title("Chat App")

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
