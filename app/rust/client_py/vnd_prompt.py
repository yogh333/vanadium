#!/usr/bin/env python3

import logging
import os
import sys
import shlex
import time

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory

from argparse import ArgumentParser
from typing import Optional

from client import Client, dotdict
from boiler_pb2 import Response

# TODO: make a proper package for the stream.py module
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "..", "..", "..", "host"))

import stream  # noqa: E402

class ActionArgumentCompleter(Completer):
    ACTION_ARGUMENTS = {
        "get_version": [],
        "get_appname": [],
        "get_pubkey": [ "display", "path="],
        "sign_tx": ["path", "to", "amount", "memo"],
    }

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        if ' ' not in document.text:
            # user is typing the action
            for action in self.ACTION_ARGUMENTS.keys():
                if action.startswith(word_before_cursor):
                    yield Completion(action, start_position=-len(word_before_cursor))
        else:
            # user is typing an argument, find which are valid
            action = document.text.split()[0]
            for argument in self.ACTION_ARGUMENTS.get(action, []):
                if argument not in document.text and argument.startswith(word_before_cursor):
                    yield Completion(argument, start_position=-len(word_before_cursor))


if __name__ == "__main__":
    parser: ArgumentParser = stream.get_stream_arg_parser()
    
    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    
    logging.basicConfig(level=log_level, format="%(asctime)s.%(msecs)03d:%(name)s: %(message)s", datefmt="%H:%M:%S")
    
    actions = ["get_version", "get_appname", "get_pubkey", "sign_tx"]

    completer = ActionArgumentCompleter()
    # Create a history object
    history = FileHistory('.cli-history')
    
    with stream.get_streamer(args) as streamer:
        cli = Client(streamer)

        last_command_time = None
        while True:
            input_line = prompt(">> ", history=history, completer=completer)

            # Split into a command and the list of arguments
            try:
                input_line_list = shlex.split(input_line)
            except ValueError as e:
                print(f"Invalid command: {str(e)}")
                continue

            # Ensure input_line_list is not empty
            if input_line_list:
                action = input_line_list[0]
            else:
                print("Invalid command")
                continue

            # Get the necessary arguments from input_command_list
            args_dict = dotdict({})
            for item in input_line_list[1:]:
                key, value = item.split('=', 1)
                args_dict[key] = value

            if action == "time":
                print("Runtime of last command:", last_command_time)
                continue

            if action not in actions:
                print("Invalid action")
                continue

            try:
                method_name = f"{action}_prepare_request"
                prepare_request = getattr(cli, method_name)

                request = prepare_request(args_dict)

                time_start = time.time()
                data: Optional[bytes] = cli.exchange_message(request)
                last_command_time = time.time() - time_start

                response = Response()
                response.ParseFromString(data)

                if response.WhichOneof("response") == "error":
                    print(f"Error: {response.error.error_msg}")
                else:
                    method_name = f"{action}_parse_response"
                    parse_response = getattr(cli, method_name)

                    parse_response(response)
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                raise e
