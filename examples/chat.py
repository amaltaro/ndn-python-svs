#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import json
import logging
import random
import subprocess
import sys
import socket
import threading
from argparse import ArgumentParser, SUPPRESS
from typing import List, Callable, Optional
# NDN Imports
from ndn.encoding import Name

# Custom Imports
sys.path.insert(0, '.')
from src.ndn.svs import SVSyncShared_Thread, SVSyncBase_Thread, SVSyncLogger, MissingData, AsyncWindow


HOST = "127.0.0.1"
PORT = random.randint(50401, 50499)
JSON_FILE = ""


def parse_cmd_args() -> dict:
    # Command Line Parser
    parser = ArgumentParser(add_help=False, description="An SVS Chat Node capable of syncing with others.")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    informationArgs = parser.add_argument_group("information arguments")
    # Adding all Command Line Arguments
    requiredArgs.add_argument("-n", "--nodename", action="store", dest="node_name", required=True,
                              help="id of this node in svs")
    optionalArgs.add_argument("-gp", "--groupprefix", action="store", dest="group_prefix", required=False,
                              help="overrides config | routable group prefix to listen from")
    informationArgs.add_argument("-h", "--help", action="help", default=SUPPRESS,
                                 help="show this help message and exit")
    # Getting all Arguments
    argvars = parser.parse_args()
    args = {}
    args["group_prefix"] = argvars.group_prefix if argvars.group_prefix is not None else "/svs"
    args["node_id"] = argvars.node_name

    # FIXME hack to get the sync messages into the display GUI
    global JSON_FILE
    JSON_FILE = args["node_id"] + ".json"

    return args


def on_missing_data(thread: SVSyncBase_Thread) -> Callable:
    taskwindow = AsyncWindow(10)

    async def wrapper(missing_list: List[MissingData]) -> None:
        async def missingfunc(nid: Name, seqno: int) -> None:
            content_str: Optional[bytes] = await thread.getSVSync().fetchData(nid, seqno, 2)
            if content_str:
                output_str: str = Name.to_str(nid) + ": " + content_str.decode()
                sys.stdout.write("\033[K")
                sys.stdout.flush()
                print(output_str)
                with open(JSON_FILE, "wt+") as jo:
                    json.dump(output_str, jo)

        for i in missing_list:
            while i.lowSeqno <= i.highSeqno:
                taskwindow.addTask(missingfunc, (Name.from_str(i.nid), i.lowSeqno))
                i.lowSeqno = i.lowSeqno + 1

    return wrapper


class Program:
    def __init__(self, args: dict) -> None:
        self.args = args
        self.svs_thread: SVSyncShared_Thread = SVSyncShared_Thread(Name.from_str(self.args["group_prefix"]),
                                                                   Name.from_str(self.args["node_id"]),
                                                                   on_missing_data,
                                                                   self.args["cache_data"])
        self.svs_thread.daemon = True
        self.svs_thread.start()
        self.svs_thread.wait()
        print(f'SVS chat client started | {self.args["group_prefix"]} - {self.args["node_id"]} |')

    def run(self) -> None:
        while 1:
            try:
                val: str = input("")
                sys.stdout.write("\033[F" + "\033[K")
                sys.stdout.flush()
                if val.strip() != "":
                    print("YOU: " + val)
                    self.svs_thread.publishData(val.encode())
                    self.send_to_client(val)
            except KeyboardInterrupt:
                sys.exit()


    def start_socket_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f'server listening on: {HOST}:{PORT}')
        while True:
            client, address = server.accept()
            self.client_socket = client
            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            client_handler.start()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    if message.strip() != "":
                        print("YOU: " + message)
                        self.svs_thread.publishData(message.encode())
            except (ConnectionResetError, BrokenPipeError):
                self.client_socket = None
                break

    def send_to_client(self, message: str):
        if self.client_socket:
            try:
                self.client_socket.sendall(message.encode('utf-8'))
            except BrokenPipeError:
                self.client_socket = None


def main() -> int:
    args = parse_cmd_args()
    args["cache_data"] = True

    ###### Setup GUI
    print("Creating the GUI...")
    p = subprocess.Popen(['python3', 'examples/chat_gui.py', args["node_id"], str(PORT)])

    SVSyncLogger.config(True, None, logging.DEBUG)
    prog = Program(args)
    ### setup socket to talk to the GUI
    prog.start_socket_server()
    prog.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
