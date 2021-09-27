import argparse
from src.krilya import Krilya

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt a file or text", add_help=False)
    parser.add_argument("operation", type=str, help="Options are: keygen, encode, decode.")

    try:
        args = parser.parse_known_args()
        namespace = args[0]
    except:
        parser.print_help()
        exit()

    # Generates a new key.
    if namespace.operation == "keygen":
        keygen_parser = argparse.ArgumentParser(parents=[parser], add_help=True)
        keygen_parser.add_argument("-l", "--length", type=int, help="Specify a key length, must be a power of 2 i.e. 64, 128, 256, 512, 1024")
        keygen_parser.add_argument("-o", "--output", type=str, help="A file to output the key to")
        keygen_parser.add_argument("-s", "--silent", help="Print the key to screen", action="store_true")
        keygen_args = keygen_parser.parse_args()
        
        k = Krilya()
        size = keygen_args.length if keygen_args.length else 256 

        if size and not ((size & (size - 1) == 0)):
            exit("Size must be a power of 2 i.e. 64, 128, 256, 512, 1024")
        target = keygen_args.output if keygen_args.output else ""
        key = k.keygen(size=size, target=target)

        if not keygen_args.silent:
            print(key)

    # Encodes a file or string.
    elif namespace.operation == "encode":
        encode_parser = argparse.ArgumentParser(parents=[parser])
        encode_parser.add_argument("-i", "--input", help="A file to read in as source")
        encode_parser.add_argument("-o", "--output", help="A file to output the results to")
        encode_parser.add_argument("-k", "--key", help="A key file to encode, otherwise uses an instance key (not recommended!)", default="")
        encode_parser.add_argument("-p", "--password", help="An optional password to apply to the encoding", default="")
        encode_parser.add_argument("-t", "--text", help="Some text to encode if no file is present.")
        encode_parser.add_argument("-s", "--silent", help="Prevents the results from being printed to screen.", action="store_true")
        encode_parser.parse_args()
        encode_args = encode_parser.parse_args()

        if not encode_args.input and not encode_args.text:
            print(encode_parser.format_help())
            exit("Either the --text (-t) or --input options must be included")

        # Encode the input file.
        elif encode_args.input:
            k = Krilya()

            # Generate a new key if none has been already.
            key = ""
            if not encode_args.key:
                key = k.keygen()
            else: 
                with open(encode_args.key) as keyfile:
                    key = "".join([line.rstrip() for line in keyfile.readlines()])

            if encode_args.output:
                print("Output will be written to {}\n".format(encode_args.output))
            else:
                print("No output selected, encoded output will be written to {}.kr\n".format(encode_args.input))
            if not encode_args.key:
                print("\nA new key was generated, save this to decode later:\n{} \n".format(k.key))

            encoded = k.encodeFile(encode_args.input, target=encode_args.output, key=key, password=encode_args.password)

        # Encode if we have text.
        elif encode_args.text:
            k = Krilya()

            # Generate a new key if none has been already.
            if not encode_args.key:
                key = k.keygen()
            else:
                with open(encode_args.key) as keyfile:
                    key = "".join([line.rstrip() for line in keyfile.readlines()])

            encoded = k.encode(encode_args.text, binary=False, key=key, password=encode_args.password)
            if not encode_args.silent:
                print("The text was encoded as followed:")
                print(encoded)
            if encode_args.output:
                with open(encode_args.output, "w+") as output:
                    output.writelines(encoded)
            if not encode_args.key:
                print("\nA new key was generated, save this to decode later:\n{} \n".format(k.key))

    elif namespace.operation == "decode":
        decode_parser = argparse.ArgumentParser(parents=[parser])
        decode_parser.add_argument("-i", "--input", help="A file to read in as source")
        decode_parser.add_argument("-o", "--output", help="A file to output the results to")
        decode_parser.add_argument("-k", "--key", help="A key file to decode the text or file with")
        decode_parser.add_argument("-p", "--password", help="An optional password to apply to the encoding", default="")
        decode_parser.add_argument("-t", "--text", help="Some text to encode if no file is present.")
        decode_parser.add_argument("-s", "--silent", help="Prevents the results from being printed to screen.", action="store_true")
        decode_parser.parse_args()
        decode_args = decode_parser.parse_args()

        if not decode_args.key:
            exit("The key -k (--key) option must be present to decode\n")
        
        if decode_args.input:
            if not decode_args.output:
                exit("The output file option is required -o (--output) when decoding a file.")
            k = Krilya()

            key = ""
            with open(decode_args.key) as keyfile:
                key = "".join([line.rstrip() for line in keyfile.readlines()])
            k.decodeFile(decode_args.input, decode_args.output, key, decode_args.password)
            print("File saved to {}".format(decode_args.output))
            exit()
        elif decode_args.text:
            k = Krilya()
            key = ""
            with open(decode_args.key) as keyfile:
                key = "".join([line.rstrip() for line in keyfile.readlines()])
            decoded = k.decode(decode_args.text, False, key, decode_args.password)
            if not decode_args.silent:
                print("The text was decoded as followed:")
                print(decoded)
            if decode_args.output:
                with open(decode_args.output, "w+") as output:
                    output.writelines(decoded)
                    print("Output written to {}".format(decode_args.output))
