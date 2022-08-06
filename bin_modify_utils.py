import json
import random

from base64 import b64decode, b64encode
from datetime import datetime

from amiibo import AmiiboMasterKey

from ssbu_amiibo import InvalidAmiiboDump
from ssbu_amiibo import SsbuAmiiboDump as AmiiboDump

# Got yelled at for having all of these classes inheret from binutils but idrc
# it makes the code cleaner imo

class BinUtils:
    def __init__(self):
        with open('keys/key_retail.bin', 'rb') as keys:
            self.keys = AmiiboMasterKey.from_combined_bin(keys.read())

    def open_dump(self, dump):
        """Opens the given data in the AmiiboDump class.
        Args:
            dump (bytes): A bytes-like object.
        Raises:
            InvalidAmiiboDump: Raises InvalidAmiiboDump if it cannot load the data.
        Returns:
            AmiiboDump: Dump of the given data.
        """
        bin_dump = dump
        # If the bin has a length of 540, pass it right into the amiibodump class
        if len(bin_dump) == 540:
            dump = AmiiboDump(self.keys, bin_dump)
            return dump
        # If the bin is larger/smaller than 540, resize it to be 540
        elif 532 <= len(bin_dump) <= 572:
            if len(bin_dump) < 540:
                # add a byte to the bin until it hits 540
                while len(bin_dump) < 540:
                    bin_dump += b'\x00'
                dump = AmiiboDump(self.keys, bin_dump)
                return dump
            if len(bin_dump) > 540:
                # shave the ending bytes off of the bin
                bin_dump = bin_dump[:-(len(bin_dump) - 540)]
                dump = AmiiboDump(self.keys, bin_dump)
                return dump

        else:
            raise InvalidAmiiboDump

    def shuffle_sn(self):
        """Generates a shuffled serial number for the amiibo to use.
        Returns:
            str: A string of bytes separated by spaces.
        """
        serial_number = "04"
        while len(serial_number) < 20:
            temp_sn = hex(random.randint(0, 255))
            # removes 0x prefix
            temp_sn = temp_sn[2:]
            # creates leading zero
            if len(temp_sn) == 1:
                temp_sn = '0' + temp_sn
            serial_number += ' ' + temp_sn
        return serial_number

class Ryujinx(BinUtils):
    def __init__(self):
        super().__init__()

    def open_dump(self, dump):
        """Opens the given data in the AmiiboDump class.
        Args:
            dump (bytes): A bytes-like object.
        Raises:
            InvalidAmiiboDump: Raises InvalidAmiiboDump if it cannot load the data.
        Returns:
            AmiiboDump: Dump of the given data.
        """
        return super().open_dump(dump)

    def shuffle_sn(self):
        """Generates a shuffled serial number for the amiibo to use.
        Returns:
            str: A string of bytes separated by spaces.
        """
        return super().shuffle_sn()

    def gen_random_bytes(self, byte_amt: int):
        generated_bytes = ""
        while len(generated_bytes) < byte_amt * 2:
            temp_gen = hex(random.randint(0, 255))
            temp_gen = temp_gen[2:]
            if len(temp_gen) == 1:
                temp_gen = '0' + temp_gen
            generated_bytes += temp_gen
        return generated_bytes

    def generate_bin(self):
        # start off with a fully 0'd out 540 byte block
        bin = bytes.fromhex('00' * 540)
        # initialize the dump, and set is_locked to false so it doesn't verify anything yet
        dump = AmiiboDump(self.keys, bin, False)
        dump.uid_hex = self.shuffle_sn()
        dump.amiibo_nickname = 'Ryujinx'
        # internal + static lock
        dump.data[0x09:0x0C] = bytes.fromhex('480FE0')
        # CC
        dump.data[0x0C:0x10] = bytes.fromhex('F110FFEE')
        # 0xA5 lol
        dump.data[0x10] = 0xA5
        # write counter
        dump.data[0x11:13] = bytes.fromhex(self.gen_random_bytes(2))
        # settings
        dump.data[0x14:0x16] = bytes.fromhex('3000')
        # crc counter
        dump.data[0x16:0x18] = bytes.fromhex(self.gen_random_bytes(2))
        # last write date
        dump.data[0x1A:0x1C] = bytes.fromhex(self.gen_random_bytes(2))
        # owner mii
        dump.data[0xA0:0x100] = bytes.fromhex('03 00 00 40 EB A5 21 1A E1 FD C7 59 D0 5A A5 4D 44 0D 56 BD 21 CA 00 00 00 00 4D 00 69 00 69 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 40 00 00 21 01 02 68 44 18 26 34 46 14 81 12 17 68 0D 00 00 29 00 52 48 50 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 14 6C'.replace(' ', ''))
        # application titleid
        dump.data[0x100:0x108] = bytes.fromhex('01006A803016E000')
        # 2nd write counter
        dump.data[0x108:0x10A] = bytes.fromhex(self.gen_random_bytes(2))
        # dynamic lock + rfui
        dump.data[0x208:0x20C] = bytes.fromhex('01000FBD')
        # cfg0 + cfg1
        dump.data[0x20c:0x214] = bytes.fromhex('000000045F000000')
        # 2 extra bytes get added somewhere, i cant figure out where so i just remove them for now
        dump.data = dump.data[:-2]
        return dump

    def bin_to_json(self, data):
        # initialize a dict to hold all of the data
        basejson = {}
        dump = self.open_dump(data)
        dump.unlock()
        # fileversion is always 0
        basejson['FileVersion'] = 0
        # amiibo name
        basejson['Name'] = dump.amiibo_nickname
        # uuid
        basejson['TagUuid'] = b64encode(dump.data[0x0:0x08]).decode('ASCII')
        # ID of the amiibo
        basejson['AmiiboId'] = dump.data[84:92].hex()
        # first write date
        basejson['FirstWriteDate'] = datetime.now().isoformat()
        # last write date
        basejson['LastWriteDate'] = datetime.now().isoformat()
        # write counter
        basejson['WriteCounter'] = dump.write_counter
        # applicationarea + app id
        basejson['ApplicationAreas'] = [
            {
                "ApplicationAreaId": int(dump.app_id.hex(), 16),
                "ApplicationArea": b64encode(dump.app_area).decode('ASCII'),
            }
        ]
        return json.dumps(basejson, indent=4), basejson["AmiiboId"]

    def json_to_bin(self, ryujinx_json):
        # loads the given json data
        ryujinx_json = json.loads(ryujinx_json)
        # generate a bin
        dump = self.generate_bin()
        # write the name to the bin if it exists
        if 'Name' in ryujinx_json:
            dump.amiibo_nickname = ryujinx_json['Name']
        # write the character to the bin
        dump.data[84:92] = bytes.fromhex(ryujinx_json['AmiiboId'])
        # write counter
        dump.write_counter = ryujinx_json['WriteCounter']
        # write apparea stuff
        if len(ryujinx_json['ApplicationAreas']) != 0:
            dump.app_id = ryujinx_json['ApplicationAreas'][0]['ApplicationAreaId'].to_bytes(4, 'big')
            dump.app_area = b64decode(ryujinx_json['ApplicationAreas'][0]['ApplicationArea'])
        dump.lock()
        return dump.data
