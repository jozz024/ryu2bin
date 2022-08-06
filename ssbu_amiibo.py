from amiibo import AmiiboDump
from amiibo.crypto import AmiiboBaseError

class InvalidAmiiboDump(AmiiboBaseError):
    pass
class IncorrectGameDataIdException(Exception):
    pass


class InvalidSsbuChecksum(Exception):
    pass


class SsbuAmiiboDump(AmiiboDump):
    """
    Class that holds a bunch of properties not published to the pip version.
    """
    @property
    def amiibo_nickname(self):
        # TODO: why is the Amiibo nickname big endian,
        # but the Mii nickname litle endian?
        return self.data[0x020:0x034].decode('utf-16-be').rstrip('\x00')

    @amiibo_nickname.setter
    def amiibo_nickname(self, name):
        utf16 = name.encode('utf-16-be')
        if len(utf16) > 20:
            raise ValueError
        self.data[0x020:0x034] = utf16.ljust(20, b'\x00')

    @property
    def app_id(self):
        return self.data[0x10a:0x10e]

    @app_id.setter
    def app_id(self, value):
        if len(value) != 4:
            raise ValueError
        self.data[0x10a:0x10e] = value

    @property
    def write_counter(self):
        return (self.data[0x108] << 8) | self.data[0x109]

    @write_counter.setter
    def write_counter(self, counter):
        if counter < 0 or counter > 0xFFFF:
            raise ValueError
        self.data[0x108] = (counter >> 8) & 0xFF
        self.data[0x109] = (counter >> 0) & 0xFF

    @property
    def app_area(self):
        return self.data[0x130:0x208]

    @app_area.setter
    def app_area(self, app_area):
        self.data[0x130:0x208] = app_area
