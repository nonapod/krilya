[![Build Status](https://app.travis-ci.com/nonapod/krilya.svg?branch=main)](https://app.travis-ci.com/nonapod/krilya)

# Krilya
Krilya is a small encryption utility that I created when deciding to tackle the idea of encryption. This contains the krilya library and also a command line python file called `run.py` than can be used to encode, decode or generate keys.  

### Key Gen
In theory a key can be anything that can be loaded in as text, as default there is a 
small keygen function to create a long string of characters of 64 length or any powers
of two i.e 64, 128, 512, 1024, 2048, 4096.

### Key Chains
A key chain is just the key broken up into multiple rows and columns, a multidimensional matrix,
this is so a password can shuffle the key chain if using a password, which will muddle up the 
rows and the col positions.

### Encoding
Encoding works by taking the first int character in the source string, can be binary which means
the char will already be represented by the digit. It adds the character int of the first position
of the keychain to it (this is called the shift position which always begins at [0][0] and then multiplies by it. 

Let's picture the key and key_chain looking something like this (it's not the most secure of keys!):
abc123def
["a", "b", "c"]
["1", "2", "3"]
["d", "e", "f"]

Let's say we want to encode the string "Hello"

Our formula is something like this:
(a + b) * b
a = source character integer
b = shift character integer

We begin by getting the int val of H: 72
We then take the first position of the keys value a: 97
We add these together and then multiple by the first position again:
(72 + 97) * 97 = 16393

That number is then turned into hexidecimal 0x4009

Now we have to shift along the table, this means we take the number of the first
position character "a": 97, and move that many times along the key chain, across
all the characters in the rows to the end, and then back, until we've rolled it that
many times. 

So the next character in the key chain will be 2: 50
We then perform the same calculation as before except we change the source character integer
and the shift character integer.
e: 101
2: 50
(101 + 50) * 50 = 7550

So lets just do all of them below now you get the idea:
H = (72 + 97) * 97 = 16393 = 0x4009
e =(101 + 50) * 50 = 7550 = 0x1E46
l = (108 + 102) * 102 = 21420 = 0x53AC
l = (108 + 97) * 97 = 19885 = 0x4D8F
o = (111 + 50) * 50 = 8050 = 0x1F72

Here is our final encrypted string:
0x40090x1E460x53AC0x4D8F0x1F72

The Krilya app by default will take that and turn it into binary and then ZLIB compress it into a 
file.

This can include any characters, it can encrypt en entire PDF file containing War and Peace in Russian
Cyrillic characters, a manifesto written in Chinese an MP3 etc... 


### Decoding
Decoding is quite simple, all we do is we convert the text again until we get our hex numbers, so let's
say we've imported the the text from the file 0x40090x1E460x53AC0x4D8F0x1F72 decompressed by ZLIB from
binary, we then begin with the first position of the key chain again.
Except this time our formula looks something like this:
(a / b) - b
a = source character integer
b = shift character integer

H = (16393 / 97) - 97 = 72
e =(7550 / 50) - 50 = 101
l = (21420 / 102) - 102 = 108
l = (19885 / 97) - 97 = 108
o = (8050 / 50) - 50 = 111

So provided we have a decent length key with all sorts of characters in it, we can get quite a random
encryption. This is also compounded with the use of a password, which will roll the position of the
key chain, which will be explained next.

### Password
A password can be provided along with the key, the password performs a shuffle of the key chain.
It does it by taking every odd character and moving the table up n amount of times, and every even
character it moves every column in each row across n amount of times.
N is equal to the number representation of the character with a modulus of 256 or whatever modulus
is provided. This means that all characters could be used to represent a password without causing
the process to take too long.

Shuffling up on an odd character means poping the key chain and pushing it to the front of the list.
Shuffling across on an even character means poping each column position of each key chain row to the front of each list.
This is repeated on each character as many times as the character in number.

What this will do is completely randomize the key chain, not only will you need a key to decode the
file, you will also need a password.


### Public/Private Keys
This hasn't been implemented...
