import binascii


import crcmod

from vrc_t70.response import VrcT70Response


def bytearray_to_response(data, contains_crc=True):
    if type(data) is str:
        data = binascii.unhexlify(str(data).lower().encode("ascii"))

    res = VrcT70Response()

    res.address = data[0]
    res.id_event = data[1]
    res.sequence_id = (data[2] << 8) | (data[3])
    res.processing_result = data[4]

    max_length_without_data = 6 if contains_crc else 5

    if len(data) > max_length_without_data:
        if contains_crc:
            res.data = data[max_length_without_data: -1]
        else:
            res.data = data[max_length_without_data + 1:]

    if contains_crc:
        res.crc = data[-1]
    else:
        crc_func = crcmod.mkCrcFun(poly=0x1d5, initCrc=0, rev=False, xorOut=0)
        res.crc = crc_func(data)

    assert res.is_crc_valid()
    return res
