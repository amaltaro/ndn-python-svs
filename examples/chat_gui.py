import argparse
import json
import sys
import tkinter as tk


def parse_cmd_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GUI for an SVS Chat application")
    parser.add_argument("-n", "--nodename", action="store", dest="node_name",
                        required=True, help="id of this node in svs")
    parser.add_argument("-gp", "--groupprefix", action="store", dest="group_prefix",
                        required=True, help="overrides config | routable group prefix to listen from")
    args = parser.parse_args()
    return args


class Chat_App(tk.Tk):

    def __init__(self, node_name, group_prefix):
        """Start a very basic tkinter window"""
        super().__init__()
        self.node_name = node_name
        self.node_input_file = f"{node_name}_input.json"
        self.node_output_file = f"{node_name}_output.json"
        self.group_prefix = group_prefix

        # set up the window title
        self.title("NDN SVS Chat application.")

        # basic configuration
        tk.Message(self, text=f"Group prefix: {group_prefix}", width=50).grid(row=0, column=0)
        tk.Message(self, text=f"Node name:    {node_name}", width=50).grid(row=1, column=0)

        # now clear files to be used
        self._clear_files()

        # variable to keep the last message received in the group
        self.last_msg = dict()

    def _clear_files(self):
        """Clear files to be used as a pipeline"""
        with open(self.node_input_file, "w+") as jo:
            json.dump({}, jo)
        with open(self.node_output_file, "w+") as jo:
            json.dump({}, jo)

    def __call__(self, *args, **kwargs):
        """Create objects of the root window and set actions"""
        self.chat_msg = tk.Text(self, width=50)
        self.chat_msg.grid(row=2, column=0, padx=10, pady=10)

        self.user_msg = tk.Entry(self, width=50)
        self.user_msg.grid(row=3, column=0, padx=10, pady=10)
        self.user_msg.insert(tk.END, "Your message")

        self.send_msg = tk.Button(self, text="Send", width=20, command=self.send_message)
        self.send_msg.grid(row=4, column=0, padx=10, pady=10)
        # callback function for when the user hits return
        # self.send_msg.bind('<Key-Return>', self.send_message)

    def send_message(self):
        """Send message to the group and to the chat frame"""
        user_msg = self.user_msg.get()
        msg = f"\n{self.node_name}: {user_msg}"
        self.chat_msg.insert(tk.END, msg)
        # now write to the file
        self._send_message(user_msg)

    def _send_message(self, message):
        """Actually write to the file pipeline"""
        with open(self.node_output_file, "wt") as jo:
            json.dump({"node_name": self.node_name, "message": message}, jo)

    def recv_message(self):
        """Receive messages from the group and write to the chat frame"""
        recv_msg = self._recv_message()
        if recv_msg:
            msg = f"\n{recv_msg['node_name']}: {recv_msg['message']}"
            self.chat_msg.insert(tk.END, msg)

    def _recv_message(self):
        """Receive messages from the group and write to the chat frame"""
        with open(self.node_input_file, "rt") as jo:
            data = json.load(jo)
        if data == self.last_msg:
            return {}
        else:
            if "node_name" not in data or "message" not in data:
                print(f"ERROR: received data in a wrong format. Data is: {data}")
                return {}
            else:
                return data


def main() -> int:
    args = parse_cmd_args()

    chat_app = Chat_App(args.node_name, args.group_prefix)
    chat_app()
    chat_app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
