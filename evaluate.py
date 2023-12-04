import subprocess
import sys
import time
import json
from random import randint

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
        node_name = f'node_{i}'
        p = subprocess.Popen(['python3', 'chat.py', '-gp', group_prefix, '-n', node_name])
        clients.append(p)
    return clients

def compare_messages(num_nodes):
    history_file = 'history.json'
    # Load the group history from history.json
    with open(history_file, 'r') as f:
        history_messages = set(json.load(f))

    for i in range(1, num_nodes + 1):
        node_name = f'node_{i}'
        with open(f'{node_name}.json', 'r') as f:
            node_messages = set(json.load(f))

            missing_in_node = history_messages - node_messages
            extra_in_node = node_messages - history_messages

            if missing_in_node or extra_in_node:
                print(f'Differences for {node_name}:')
                if missing_in_node:
                    print(f' - Missing in node: {missing_in_node}')
                if extra_in_node:
                    print(f' - Extra in node: {extra_in_node}')
            else:
                print(f'No differences for {node_name}')


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
