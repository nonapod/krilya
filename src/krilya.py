from os import name
import random
import zlib
import argparse
import sys

class Krilya():
    """
    Krilya is an encryption utility
    """

    def __init__(self, **kwargs):
        self.key_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+='
        self.key = ''
        self.key_chain_table_size = 10
        self.password_mod = 256 # a password character i.e a Russian character of 1023 for instance
                                # will get the modulus from the ascii table.

        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])

    def decode(self, source, binary=False, key="", password=""):
        """
        decodes the source text. binary mode can be set if we want
        the result to be an array of binary ints. an key can be used
        optionally otherwise it defaults to the instance key.
        :param source: string the source string
        :param binary: boolean whether or not we want an array of digits returned or not for use in binary.
        :param key: string optional key or else uses instance key
        :param password: string an optional password which will affect the chain
        :return: array or string
        """
        if not key:
            key = self.key
        assert key

        key_chain = self.keychain(key=key, password=password)

        source = source.split("0x")
        if binary:
            decoded_source = []
        else:
            decoded_source = ""
        chain_row = 0
        chain_pos = 0
        shift = 0

        for ch in source:
            if ch:
                # get the next shift digit (how many digits along in the chain we move for the next pos scramble)
                chain_row, chain_pos = self.reshift(shift, chain_pos, chain_row, len(key_chain), key=key)
                # get the hex value of the current character in the source
                char_code = int(ch, 16)
                # get the character number of the current shift position in the key, begins at the first position of the key
                key_char_code = ord(str(key_chain[chain_row][chain_pos]))
                if binary:
                    # we reverse the encoding calculation by dividing the character code by the current shift
                    # position characters int value and then add the key_char_code value.
                    decoded_char = int((char_code/key_char_code-key_char_code))
                    decoded_source.append(decoded_char)
                else:
                    decoded_char = chr(int((char_code/key_char_code-key_char_code)))
                    decoded_source += decoded_char
                shift = char_code

        return decoded_source


    def encode(self, source, binary=False, key="", password=""):
        """
        encode either in binary or regular text format, binary
        is preferable. takes in text and returns it either an
        encrypted string or an array of ints if in binary mode. a
        key can be passed optionally or else the current instance
        key will be used.
        :param source: string the source string
        :param binary: boolean whether or not we want an array of digits returned or not for use in binary.
        :param key: string optional key or else uses instance key
        :param password: string an optional password which will affect the chain
        :return: array or string
        """
        if not key:
            key = self.key
        assert key

        key_chain = self.keychain(key=key, password=password)
        if binary:
            encoded_source = []
        else:
            encoded_source = ""

        chain_row = 0
        chain_pos = 0
        shift = 0

        for ch in source:
            # get the next shift digit (how many digits along in the chain we move for the next pos scramble)
            chain_row, chain_pos = self.reshift(shift, chain_pos, chain_row, len(key_chain), key=key)
            if binary:
                char_code = ch
            else:
                char_code = ord(ch)

            # get the character number of the current shift position in the key, begins at the first position of the key
            key_char_code = ord(str(key_chain[chain_row][chain_pos]))
            # encode the character by adding the source character to the shift position character and then multiplying my the shift position character
            encoded_char = int((char_code+key_char_code)*(key_char_code))
            # set the shift character to be the value of the current key character number
            shift = encoded_char
            # get the encoded char in hex format
            encoded_char = hex(encoded_char)

            if binary:
                encoded_source.append(encoded_char)
            else:
                encoded_source += "%s" % (encoded_char)

        return encoded_source


    def reshift(self, shift, chain_pos, chain_row, chain_length, key=""):
        """
        takes a shift value along with the current chain row and pos
        as well as the chain length itself, and returns a tuple containing
        the chain row and chain pos. the shift is how many characters along
        in the key chain we will jump to give our calculation to scramble/unscramble
        the next character.
        :param shift: int a value to move along by
        :param chain_pos: int the current chain position
        :param chain_row: int the current chain row
        :param chain_length: int the length of the key chain.
        :return: tuple
        """
        if not key:
            key = self.key
        assert key

        if shift:
            # the shift digit is the remainder of the shift digit divided by the key length
            shift = shift % len(key)
            # get the number of available columns
            columns = int(len(key) / self.key_chain_table_size)
            # using the shift digit, determine the row and col pos in the keychain
            chain_row = int(shift/columns)
            chain_pos = int(shift%columns)
            # return to the first row if the row exceeds the available rows
            if chain_row > chain_length - 1:
                chain_row = 0

        return (chain_row, chain_pos)



    def keygen(self, size=256, target=""):
        """
        creates a key of size greater than 128, must be a power of 2
        i.e. 128, 256, 512
        :param size: int key size, must be a power of 2 and greater than 64
        :param target: string dump the key to a file
        :return: tuple
        """
        if not size < 64 and size != 0 and ((size & (size - 1) == 0)):
            key = "".join(random.choice(self.key_chars) for _ in range(size))
            if target:
                with open(target, "w+") as file:
                    file.writelines(key)
            return key

    def loadKey(self, source):
        """
        loads a key from a file into the instance and returns it also, requires a source target file name
        :param source: string source key file name
        """
        with open(source, 'r') as file:
            key = file.read()
            self.key = key
        return key


    def keychain(self, key="", password=""):
        """
        creates an even sized keychain based off of the current key.
        what is a keychain? a keychain is essentially the key just
        broken out into sets of rows in the form of a list. the
        keychain can be shuffled or rolled around during encoding/decoding
        when using a password.
        :param password: string an optional password which will shuffle the chain
        :return: list
        """
        if not key:
            key = self.key
        key = list(key)
        assert key

        # break out the key into a matrix row/col table
        chain_size = int(len(key) / self.key_chain_table_size)
        key_chain = [[key.pop(0) for i in range(0, chain_size)] for x in enumerate(key)]

        # if we get a password, shuffle the keychain before returning it
        if password:
            across = 0
            # loop every character in the password
            for ch in [ord(i) % self.password_mod for i in list(password)]:
                while ch > 0:
                    # if we're going across, we push the last character of each key chain row to the front of its
                    # respective row, as many times as the password character is in size
                    if across:
                        for key_chain_row_idx, key_chain_row in enumerate(key_chain):
                            key_chain[key_chain_row_idx].insert(0, key_chain[key_chain_row_idx].pop())
                    # if we're going up, we push the last row to the front of the key chain as many times
                    # as the password character is in size
                    else:
                        key_chain.insert(0, key_chain.pop())
                    across = not across
                    ch-=1

        return key_chain

    def encodeFile(self, source, target="", key="", password=""):
        """
        encodes a file by file name to target using a given key,
        uses zlib compression to keep the filesize down.
        :param source: string the source file name
        :param target: string the target file name
        :param password: string an optional password to encode with
        :param key: string optional key
        """
        if not key:
            key = self.key
        assert key

        if not target:
            target = "%s.kr" % source

        with open(source, 'rb') as bytes:
            bytes = bytes.read()
            encoding = self.encode(bytes, binary=True, key=key, password=password)

        with open(target, 'wb+') as file:
            encoded_string = "".join(encoding)
            compressed = zlib.compress(encoded_string.encode())
            file.write(compressed)

    def decodeFile(self, source, target="", key="", password=""):
        """
        decodes a file by file name to target using a given key,
        uses zlib compression to keep the filesize down.
        :param source: string source file
        :param target: string target file
        :param password: string an optional password to encode with
        :param key: string optional key
        """
        if not key:
            key = self.key
        assert key
        decoding = None

        with open(source, 'rb') as file:
            encoding = file.read()
            uncompressed = zlib.decompress(encoding)
            try:
                decoding = bytearray(self.decode(uncompressed.decode(), binary=True, key=key, password=password))
            except ValueError as e:
                if password:
                    raise Exception("Value Error decoding source, double check to make sure password or key is correct")
                else:
                    raise Exception("Value Error decoding source, double check to make sure you are using the correct key")

        if decoding:
            if target:
                with open(target, 'wb+') as file:
                    file.write(decoding)
            else:
                return decoding

    def passwordToKey(self, password):
        """
        This function allows the use of purely password authentication,
        but with no key quite a simple function, sets the first character as the key,
        then loops through each password character dividing by the keys previous
        character, then multiplying that number by the current key position modulus
        256 to keep within the bounds of ascii. It then sorts the key so the first
        character of the password isn't known. The password is what matters and
        the strength of it, a simple password will be cracked, a hard
        password not easily.
        :return: string key
        """
        assert len(password) >= 8
        password = list(password)
        password_pos = 0
        key = [password[0]]
        key_pos = 1
        while len(key) < 1024:
            if password_pos >= len(password):
                password_pos = 0

            magic_number = ord(password[password_pos])/(ord(key[key_pos-1]))
            magic_number = int((magic_number*(key_pos))%256)

            if magic_number:
                key.append(chr(magic_number))
                key_pos += 1

            password_pos += 1

        key.sort()
        return "".join(key)
