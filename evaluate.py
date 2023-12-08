import subprocess
import sys
import time
import json
from random import randint
from pprint import pformat


def start_nfd_and_set_strategy(group_prefix):
    subprocess.run(['nfd-start'], check=True)
    subprocess.run(['nfdc', 'strategy', 'set', group_prefix, '/localhost/nfd/strategy/multicast'], check=True)

def create_dataset(num_nodes, num_messages):
    """
    Given a number of nodes and messages, create a dataset in two files:
      1. dataset_orig.json: with the full dataset
      2. dataset.json: the same dataset, but actually consumed/popped
    """
    dataset = []
    for i in range(1, num_messages + 1):
        msg = f"This is message number {i}"
        node_name = f'node_{randint(1, num_nodes)}'
        dataset.append({'node_id': node_name, 'data': msg})
    with open("dataset_orig.json", "wt") as jo:
        json.dump(dataset, jo)
    with open("dataset.json", "wt") as jo:
        json.dump(dataset, jo)
    print("Two dataset files created.")

def start_chat_clients(group_prefix, num_nodes):
    clients = []
    for i in range(1, num_nodes + 1):
        time.sleep(0.5)
        node_name = f'node_{i}'
        p = subprocess.Popen(['python3', 'chat.py', '-gp', group_prefix, '-n', node_name])
        clients.append(p)
    return clients

def compare_messages(num_nodes):
    # a list of lists
    node_history = []
    print("")
    for i in range(1, num_nodes + 1):
        node_name = f"history_node_{i}.json"
        with open(node_name, 'r') as f:
            node_messages = json.load(f)
        print(f"File: {node_name} with messages:\n{pformat(node_messages)}")
        node_history.append(node_messages)

    # assume the first node has the correct history
    print("")
    messages = node_history.pop()
    msg_nodes = set([item['node_id'] for item in messages])
    msg_messages = set([item['data'] for item in messages])
    for idx, node_msg in enumerate(node_history):
        node_nodes = set([item['node_id'] for item in node_msg])
        node_messages = set([item['data'] for item in node_msg])
        missing_in_node = msg_nodes - node_nodes
        extra_in_node = node_nodes - msg_nodes

        if missing_in_node or extra_in_node:
            print(f'Differences for node_{idx+2}:')
            if missing_in_node:
                print(f' - Missing in node: {missing_in_node}')
            if extra_in_node:
                print(f' - Extra in node: {extra_in_node}')
        else:
            print(f'No differences for node_{idx+2}')


def main():
    group_prefix = sys.argv[1]
    num_nodes = int(sys.argv[2])
    num_messages = int(sys.argv[3])

    # start_nfd_and_set_strategy(group_prefix)
    create_dataset(num_nodes, num_messages)
    clients = start_chat_clients(group_prefix, num_nodes)
    time.sleep(5)  # Wait for clients to initialize
    time.sleep(10)  # Wait for messages to be sent and processed
    compare_messages(num_nodes)

    # Terminate all clients
    for client in clients:
        client.terminate()

    # subprocess.run(['nfd-stop'], check=True)

if __name__ == "__main__":
    main()
