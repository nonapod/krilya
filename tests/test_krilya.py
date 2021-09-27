import unittest 
import os
import shutil
from src.krilya import Krilya
import urllib3
import hashlib 

TEST_DATA_DIR="tests/test_data"
TEST_STR_EN = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam pellentesque pharetra sapien vitae tincidunt. Curabitur laoreet faucibus diam nec ullamcorper. Nunc molestie quam lectus, quis vulputate leo posuere ac. Quisque semper, nisi sit amet euismod scelerisque, sapien sem efficitur felis, ut tristique odio lectus in ligula. Mauris interdum dignissim enim vitae finibus. Proin volutpat porta urna. Pellentesque placerat viverra malesuada."
TEST_STR_RU = "Лорем ипсум долор сит амет, посидониум либерависсе ид про, ан лорем орнатус цивибус хис, не усу еуисмод епицуреи сенсерит. Синт ферри хас те. Идяуе вениам инимицус вих ут, ех тимеам ментитум медиоцритатем нец. Ет нихил интеллегебат хис."
TEST_STR_CN = "方情霊合全護聞集具見実真準意北年月輸容。認際送像押著代載並土信死攻社図一才省激。表呼今輪作余社線六心討支。企館供海雑務尻言高動次円報。会天湾家子最丸見資制作政重教一率負。序大済童更切報富白前年息掲入展刊負防止念。済済料申乃実停大多明員名。申村場育様嶋寒個群供材月一。陶紀常校王運民代機映弾供新載見伸和善消世。"
TEST_STR_AM = "լոռեմ իպսում դոլոռ սիթ ամեթ, պռո եու լոռեմ աուդիռե, վիս ինանի դոծթուս դելեծթուս իդ. ին նեծ քուոթ առգումենթում, հաս եթ իպսում վիռիս, եխ մենթիթում մեդիոծռիթաթեմ վիխ. ան պռոբաթուս ռաթիոնիբուս պեռսեքուեռիս հաս. եամ իդ վիվենդո սենսեռիթ, եոս լոռեմ մինիմ լեգեռե իդ. ելիթ ինվիդունթ ծու սեդ, վեռիթուս ռաթիոնիբուս վիթուպեռաթա դուո իդ. սեա նո ծլիթա նոլուիսսե, սեա պեռթինախ ինդոծթում քուաեռենդում աթ, նե վել ծիբո ռեպռեհենդունթ."
TEST_STR_IN = "उनको अधिकार शारिरिक पुर्णता ध्वनि तकरीबन विनिमय भाषाओ भाति उदेशीत वर्णित गोपनीयता रिती विवरण सुनत शुरुआत गटकउसि स्थापित विशेष अर्थपुर्ण माहितीवानीज्य प्राण हीकम अन्य शीघ्र दिशामे अंतर्गत संस्थान ध्येय क्षमता प्रतिबध वार्तालाप अन्य आवश्यकत व्रुद्धि नवंबर उनका जिसकी वर्ष पत्रिका प्रव्रुति पुष्टिकर्ता ढांचा पुस्तक नयेलिए प्रतिबध भाति शीघ्र सम्पर्क मर्यादित सकते ध्येय बहुत और्४५० लाभान्वित अमितकुमार"
TEST_STR_LIST = [
    TEST_STR_EN,
    TEST_STR_RU,
    TEST_STR_CN,
    TEST_STR_AM,
    TEST_STR_IN
]
TEST_IMG_URL = "https://picsum.photos/200/300"
TEST_IMG_PATH = os.path.join(TEST_DATA_DIR, "test.jpg")

class TestKrilya(unittest.TestCase):

    def setUp(self):
        """
        Creates the test data directory.
        """
        if not os.path.isdir(TEST_DATA_DIR):
            os.mkdir("tests/test_data")
        self.assertTrue(os.path.isdir(TEST_DATA_DIR))

    def tearDown(self):
        """
        Removes the test data directory and files.
        """
        if os.path.isdir(TEST_DATA_DIR):
            for item in os.listdir(TEST_DATA_DIR):
                os.remove(os.path.join(TEST_DATA_DIR, item))
            os.rmdir(TEST_DATA_DIR)

        self.assertFalse(os.path.isdir(TEST_DATA_DIR))

    def test_keygen_to_string(self):
        """
        Test generation of multiple keys to string, only power of 2 should work.
        """
        kriliya = Krilya()

        key = kriliya.keygen(256)
        self.assertTrue(isinstance(key, str) and len(key) == 256)

        key = kriliya.keygen(512)
        self.assertTrue(isinstance(key, str) and len(key) == 512)

        key = kriliya.keygen(1024)
        self.assertTrue(isinstance(key, str) and len(key) == 1024)

        key = kriliya.keygen(271)
        self.assertFalse(isinstance(key, str))

        key = kriliya.keygen(333)
        self.assertFalse(isinstance(key, str))

    def test_keygen_to_file(self):
        """
        Test generation of multiple keys to output file.
        """
        krilya = Krilya()
        key_path = os.path.join(TEST_DATA_DIR, "test.key")
        bad_key_path = os.path.join(TEST_DATA_DIR, "test_bad.key")
        for item in [256, 512, 1024]:
            # Generate the test key.
            key = krilya.keygen(item, target=key_path)
            self.assertTrue(os.path.isfile(key_path))

            # Open the keys, make sure they are of the right length.
            with open(key_path) as key_file:
                key = key_file.readline().rstrip()
                self.assertTrue(len(key) == item)
        
        for item in [111, 411, 677]:
            # Generate a bad test key.
            key = krilya.keygen(item, target=bad_key_path)
            self.assertFalse(os.path.isfile(bad_key_path))
    
    def test_encode_decode_str(self):
        """
        Test encoding a string with a key from file and key from str.
        """
        krilya = Krilya()
        key_path = os.path.join(TEST_DATA_DIR, "test_encode_decode.key")

        # Test key string.
        key = krilya.keygen(256)
        for lang_str in TEST_STR_LIST:
            encoded = krilya.encode(lang_str, binary=False, key=key)
            self.assertFalse(encoded == lang_str)
            decoded = krilya.decode(encoded, binary=False, key=key)
            self.assertTrue(decoded == lang_str)

            # Try to decode with a bad key, skip the exception and make sure it
            # doesn't match the original string.
            bad_decoded = ""
            try:
                bad_decoded = krilya.decode(encoded, binary=False, key="opiu9dsa7u98")
            except:
                pass
            self.assertFalse(bad_decoded == lang_str)
        
        # Test key file.
        key = ""
        krilya.keygen(256, target=key_path)
        with open(key_path) as key_file:
            key = key_file.readline().rstrip()
        self.assertTrue(len(key) == 256)

        for lang_str in TEST_STR_LIST:
            encoded = krilya.encode(lang_str, binary=False, key=key)
            self.assertFalse(encoded == lang_str)
            decoded = krilya.decode(encoded, binary=False, key=key)
            self.assertTrue(decoded == lang_str)

            # Try to decode with a bad key, skip the exception and make sure it
            # doesn't match the original string.
            bad_decoded = ""
            try:
                bad_decoded = krilya.decode(encoded, binary=False, key="opiu9dsa7u98")
            except:
                pass
            self.assertFalse(bad_decoded == lang_str)

    
    def test_encode_decode_str_password(self):
        """
        Tests encoding and decoding a string with accompanying password.
        """
        krilya = Krilya()
        password = "%^829813712987(*^#!@^Q09712089021380912309q7(*&"

        # Test key string.
        key = krilya.keygen(256)
        for lang_str in TEST_STR_LIST:
            encoded = krilya.encode(lang_str, binary=False, key=key, password=password)
            self.assertFalse(encoded == lang_str)
            decoded = krilya.decode(encoded, binary=False, key=key, password=password)
            self.assertTrue(decoded == lang_str)

            # Try to perform a bad decoding, skip the thrown exception and make sure
            # it doesn't equal the original string.
            bad_decoded = ""
            try:
                bad_decoded = krilya.decode(encoded, binary=False, key=key, password="aoiu2983o")
            except:
                pass
            self.assertFalse(bad_decoded == lang_str)
        
    def test_encode_decode_file(self):
        """
        Test encoding and decoding a file.
        """
        krilya = Krilya()
        key_path = os.path.join(TEST_DATA_DIR, "test_encode_decode_file.key")
        test_file_path = os.path.join(TEST_DATA_DIR, "test_encoding.txt")
        test_encoded_file_path = os.path.join(TEST_DATA_DIR, "test_encoding.txt.kr")
        test_decoded_file_path = os.path.join(TEST_DATA_DIR, "test_decoded.txt")
        krilya.keygen(256, target=key_path)
        self.assertTrue(os.path.exists(key_path))

        # Set the key on the instance using the loadKey() function this time.
        krilya.loadKey(key_path)
        self.assertTrue(len(krilya.key) == 256)

        for lang_str in TEST_STR_LIST:
            with open(test_file_path, "w+") as test_encoding_file:
                test_encoding_file.write(lang_str)
            
            krilya.encodeFile(test_file_path)
            self.assertTrue(os.path.exists(test_encoded_file_path))
            krilya.decodeFile(test_encoded_file_path, target=test_decoded_file_path)
            self.assertTrue(os.path.exists(test_decoded_file_path))
            decoded = ""
            with open(test_decoded_file_path) as decoded_file:
                decoded = decoded_file.readline().rstrip()

            self.assertTrue(decoded == lang_str)

    def test_encode_decode_binary_file(self):
        """
        Test encoding and decoding of an image file.
        """
        # Download the test image.
        http = urllib3.PoolManager()
        with open(TEST_IMG_PATH, "wb") as img_file:
            response = http.request('GET', TEST_IMG_URL, preload_content=False)
            shutil.copyfileobj(response, img_file)

        http.clear()
        self.assertTrue(os.path.exists(TEST_IMG_PATH))

        krilya = Krilya()
        encoded_path = "%s.kr" % TEST_IMG_PATH
        decoded_path = os.path.join(TEST_DATA_DIR, "decoded_img.jpg")
        key_path = os.path.join(TEST_DATA_DIR, "test_encode_decode_binary_file.key")
        krilya.keygen(256, target=key_path)
        self.assertTrue(os.path.exists(key_path))
        krilya.loadKey(key_path)

        krilya.encodeFile(TEST_IMG_PATH)
        self.assertTrue(os.path.exists(encoded_path))

        # Hash original and encoding files, make sure they don't match.
        original_md5 = hashlib.md5()
        with open(TEST_IMG_PATH, "rb") as img_file:
            for chunk in iter(lambda: img_file.read(4096), b""):
                original_md5.update(chunk)
        original_hash = original_md5.hexdigest()

        encoded_md5 = hashlib.md5()
        with open(encoded_path, "rb") as img_file:
            for chunk in iter(lambda: img_file.read(4096), b""):
                encoded_md5.update(chunk)
        encoded_hash = encoded_md5.hexdigest()

        self.assertFalse(encoded_hash == original_hash)

        # Decode the file then compare hashes again.
        krilya.decodeFile(encoded_path, target=decoded_path)
        self.assertTrue(os.path.exists(decoded_path))

        decoded_md5 = hashlib.md5()
        with open(decoded_path, "rb") as img_file:
            for chunk in iter(lambda: img_file.read(4096), b""):
                decoded_md5.update(chunk)
        decoded_hash = decoded_md5.hexdigest()

        self.assertTrue(decoded_hash == original_hash)


if __name__ == "__main__":
    unittest.main()
