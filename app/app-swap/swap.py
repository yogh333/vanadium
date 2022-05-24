#!/usr/bin/env python3

import os
import sys

# ensure that protobuf/message_pb2.py will be found
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "host"))

# apt install python3-protobuf
from protobuf import message_pb2  # noqa: E402

import stream  # noqa: E402


class Swap:
    def init_swap_prepare_request(self) -> bytes:
        init_swap = message_pb2.RequestInitSwap()
        message = message_pb2.Request()
        message.init_swap.CopyFrom(init_swap)
        assert message.WhichOneof("message_oneof") == "init_swap"
        return message.SerializeToString()

    def init_swap_parse_response(self, data):
        response = message_pb2.Response()
        response.ParseFromString(data)
        assert response.WhichOneof("message_oneof") == "init_swap"
        print(f"response: {response.init_swap}")
        self.device_id = response.init_swap.device_id
        return response

    def swap_prepare_request(self) -> bytes:
        """get_version = message_pb2.RequestGetVersion()
        message = message_pb2.Request()
        message.get_version.CopyFrom(get_version)
        assert message.WhichOneof("message_oneof") == "get_version"
        return message.SerializeToString()"""
        with open("app/req.bin", "rb") as fp:
            data = fp.read()
        data = data.replace(b"aaaaaaaaaa", self.device_id)
        return data[4:]

    def swap_parse_response(self, data):
        response = message_pb2.Response()
        response.ParseFromString(data)
        assert response.WhichOneof("message_oneof") == "swap"
        print(f"response: {response.swap}")
        return response


if __name__ == "__main__":
    parser = stream.get_stream_arg_parser()
    parser.add_argument("--action", default="swap", choices=["swap"])
    args = parser.parse_args()

    with stream.get_streamer(args) as streamer:
        swap = Swap()

        data = streamer.exchange(swap.init_swap_prepare_request())
        swap.init_swap_parse_response(data)

        data = streamer.exchange(swap.swap_prepare_request())
        swap.swap_parse_response(data)
