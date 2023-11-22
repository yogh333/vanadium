from boiler_pb2 import RequestGetVersion, RequestGetAppName, RequestGetPubKey, RequestSignTx, Request
from util import bip32_path_to_list

ACK = b'\x42'

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Client:
    def __init__(self, streamer):
        self.streamer = streamer

    def exchange_message(self, data: bytes) -> bytes:
        # Encode the length of the data as a 4-byte big-endian integer
        length_encoded = len(data).to_bytes(4, 'big')

        # Construct the complete message
        full_message = length_encoded + data
        response_data = b''

        # Send the message in chunks of up to 256 bytes
        for i in range(0, len(full_message), 256):
            chunk = full_message[i:i+256]
            response = self.streamer.exchange(chunk)

            # If we're sending the last chunk, the response will be the start of the actual response
            # Otherwise, the response should be a single byte 0x42.
            if i + 256 >= len(full_message):
                response_data = response
            elif response != ACK:
                raise ValueError('Unexpected data received before message transmission was complete.')

        if len(response_data) < 4:
            raise ValueError('Incomplete length received in response.')

        # Extract the expected length of the full response
        response_length = int.from_bytes(response_data[:4], 'big')
        response_data = response_data[4:]

        # Continue receiving data until the full response is retrieved
        while len(response_data) < response_length:
            chunk = self.streamer.exchange(ACK)  # Request more of the response
            response_data += chunk

        # Return the complete response
        return response_data[:response_length]

    def get_version_prepare_request(self, args: dotdict):
        get_version = RequestGetVersion()
        message = Request()
        message.get_version.CopyFrom(get_version)
        assert message.WhichOneof("request") == "get_version"
        return message.SerializeToString()

    def get_version_parse_response(self, response):
        assert response.WhichOneof("response") == "get_version"
        print(f"version: {response.get_version.version}")
        return
    
    def get_appname_prepare_request(self, args: dotdict):
        get_appname = RequestGetAppName()
        message = Request()
        message.get_appname.CopyFrom(get_appname)
        assert message.WhichOneof("request") == "get_appname"
        return message.SerializeToString()

    def get_appname_parse_response(self, response):
        assert response.WhichOneof("response") == "get_appname"
        print(f"appname: {response.get_appname.appname}")
        return
    
    def get_pubkey_prepare_request(self, args: dotdict):
        get_pubkey = RequestGetPubKey()
        display_value = args.get("display", "False")
        get_pubkey.display = display_value.lower() == "true"
        get_pubkey.path.extend(bip32_path_to_list(args.get("path", "m/44'/1'/0'/0/0")))
        message = Request()
        message.get_pubkey.CopyFrom(get_pubkey)

        assert message.WhichOneof("request") == "get_pubkey"
        return message.SerializeToString()
    
    def get_pubkey_parse_response(self, response):
        assert response.WhichOneof("response") == "get_pubkey"
        print(f"pubkey (65): 0x{response.get_pubkey.pubkey}")
        print(f"chaincode (32): 0x{response.get_pubkey.chaincode}")
        return
    
    def sign_tx_prepare_request(self, args: dotdict):
        tx = RequestSignTx()
        tx.path.extend(bip32_path_to_list(args.get("path", "m/44'/1'/0'/0/0")))
        tx.nonce = 1
        tx.value = int(args.get("ammount", "666"))
        tx.address = args.get("to", "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae")
        tx.memo = args.get("memo", "For u EthDev")
        message = Request()
        message.sign_tx.CopyFrom(tx)

        assert message.WhichOneof("request") == "sign_tx"
        return message.SerializeToString()
    
    def sign_tx_parse_response(self, response):
        assert response.WhichOneof("response") == "sign_tx"
        print(f"hash: {response.sign_tx.hash}")
        print(f"len: {response.sign_tx.siglen}")
        print(f"signature (DER): 0x{response.sign_tx.sig}")
        print(f"v: 0x{response.sign_tx.v}")
        return