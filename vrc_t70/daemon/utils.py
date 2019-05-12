import binascii


def hexlify_to_string(data):
    return binascii.hexlify(data).decode("ascii")
