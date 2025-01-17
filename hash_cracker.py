#!/usr/bin/env python3

import os
import concurrent.futures
import re
import signal
import sys
import warnings
import requests
import csv
import tkinter as tk
from tkinter import filedialog

# Suppress only the single InsecureRequestWarning from urllib3 needed
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from api_handlers import alpha, beta, gamma, delta, theta, crackstation, hashes_org

# Terminal badges for output
end = '\033[0m'
red = '\033[91m'
green = '\033[92m'
yellow = '\033[93m'
info = '\033[93m[!]\033[0m'
good = '\033[92m[+]\033[0m'
bad = '\033[91m[-]\033[0m'

# Hash functions lists
md5 = [gamma, alpha, beta, theta, delta, crackstation, hashes_org]
sha1 = [alpha, beta, theta, delta, crackstation, hashes_org]
sha256 = [alpha, beta, theta, crackstation, hashes_org]
sha384 = [alpha, beta, theta, crackstation, hashes_org]
sha512 = [alpha, beta, theta, crackstation, hashes_org]

# Crack function to identify and use appropriate hash functions
def crack(hashvalue):
    length_to_funcs = {
        32: ('MD5', md5),
        40: ('SHA1', sha1),
        64: ('SHA-256', sha256),
        96: ('SHA-384', sha384),
        128: ('SHA-512', sha512)
    }
    hash_length = len(hashvalue)
    if hash_length in length_to_funcs:
        print(f'{info} Hash function : {length_to_funcs[hash_length][0]}')
        for api in length_to_funcs[hash_length][1]:
            r = api(hashvalue, length_to_funcs[hash_length][0].lower())
            if r is not None:  # Check if r is not None or not an error indicator
                return r, length_to_funcs[hash_length][0]
        print(f'{bad} Hash not found in any database.')
    else:
        print(f'{bad} This hash type is not supported.')
    return None, None

# Results dictionary
result = {}

# Threaded cracking function
def threaded(hashvalue):
    resp, algo = crack(hashvalue)
    if resp:
        print(f'{good} Original word : {resp}')
        result[hashvalue] = (resp, algo)
    else:
        print(f'{bad} Hash was not found.')

# Function to mine hashes from file
def miner(file, thread_count):
    lines = []
    found = set()
    with open(file, 'r') as f:
        lines = [line.strip('\n') for line in f]
    for line in lines:
        matches = re.findall(
            r'[a-f0-9]{128}|[a-f0-9]{96}|[a-f0-9]{64}|[a-f0-9]{40}|[a-f0-9]{32}', line)
        found.update(matches)
    print(f'{info} Hashes found: {len(found)}')
    threadpool = concurrent.futures.ThreadPoolExecutor(
        max_workers=thread_count)
    futures = [threadpool.submit(threaded, hashvalue) for hashvalue in found]
    for i, _ in enumerate(concurrent.futures.as_completed(futures)):
        if i + 1 == len(found) or (i + 1) % thread_count == 0:
            print(f'{info} Progress: {i + 1}/{len(found)}', end='\r')
    print("\n")

# Function for single hash cracking
def single(hashvalue):
    result, algo = crack(hashvalue)
    if result:
        print(f'{good} Original word : {result}')
        print("\n")
    else:
        print(f'{bad} Hash was not found in any database.')
        print("\n")

# Function to display the menu
def display_menu():
    print()
    print("╔═══════════════════════════════╗")
    print("║           DE-HASHER           ║")
    print("╠═══════════════════════════════╣")
    print("║  1. Crack a single hash       ║")
    print("║  2. Crack hashes from a file  ║")
    print("║  3. Crack hashes from CSV     ║")
    print("║  4. Exit                      ║")
    print("╚═══════════════════════════════╝")

# Timeout function using signals
class TimeoutException(Exception):
    pass

def handler(signum, frame):
    raise TimeoutException()

def input_with_timeout(prompt, timeout):
    # Set the signal handler and a timeout alarm
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)

    try:
        print(prompt)
        user_input = input()
        signal.alarm(0)  # Disable the alarm
        return user_input
    except TimeoutException:
        print(f'{bad} No selection made, terminating...')
        print("\n")
        os._exit(1)  # Exit the entire process

# Function to process CSV file for de-hashing
def process_csv(file_path, thread_count):
    hashes = []
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            if row:
                hashes.append(row[0])
    print(f'{info} Hashes found in CSV: {len(hashes)}')
    threadpool = concurrent.futures.ThreadPoolExecutor(
        max_workers=thread_count)
    futures = {hashvalue: threadpool.submit(threaded, hashvalue) for hashvalue in hashes}
    with open('dehashed_output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Function Used', 'Hashed Value', 'Original Word'])
        for hashvalue in hashes:
            futures[hashvalue].result()  # Ensure the future is completed
            if hashvalue in result:
                original_word, algo = result[hashvalue]
                writer.writerow([algo, hashvalue, original_word])
                print(f'Function used: {algo}\nHashed Value: {hashvalue}\nOriginal Word: {original_word}\n')
            else:
                print(f'{bad} Hash {hashvalue} was not found.')

# Main function
def main():
    while True:
        display_menu()
        try:
            choice = input_with_timeout(f"{info} Enter your choice (1-4): ", 10)

            if not choice:
                continue

            if choice == '1':
                hashvalue = input_with_timeout(f"{info} Enter the hash to crack: ", 15)
                if hashvalue:
                    single(hashvalue)
            elif choice == '2':
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(
                    filetypes=[("Text files", "*.txt")])
                if file_path:
                    thread_count = input_with_timeout(
                        f"{info} Enter the number of threads (default is 4): ", 10)
                    if thread_count:
                        thread_count = int(thread_count) if thread_count.isdigit() else 4
                        miner(file_path, thread_count)
                    else:
                        print(f"{bad} No thread count selected.")
                else:
                    print(f"{bad} No file selected.")
            elif choice == '3':
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(
                    filetypes=[("CSV files", "*.csv")])
                if file_path:
                    thread_count = input_with_timeout(
                        f"{info} Enter the number of threads (default is 4): ", 10)
                    if thread_count:
                        thread_count = int(thread_count) if thread_count.isdigit() else 4
                        process_csv(file_path, thread_count)
                    else:
                        print(f"{bad} No thread count selected.")
                else:
                    print(f"{bad} No file selected.")
            elif choice == '4':
                print(f"{info} Exiting...")
                break
            else:
                print(f"{bad} Invalid choice. Please enter a number between 1 and 4.")
        except TimeoutException:
            os._exit(1)  # Ensure the process exits

if __name__ == '__main__':
    main()