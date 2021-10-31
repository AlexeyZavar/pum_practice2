# AlexeyZavar ARchive
ARCHIVE_EXTENSION = 'azar'

#
# Encoding options
#
ENCODING = 'utf-8'
BYTE_ORDER = 'little'

#
# File structure options
#
MAGIC_HEADER = 'azAR'.encode(ENCODING)
MAGIC_SEPARATOR = 'RAza'.encode(ENCODING)
SYMBOL_SEPARATOR = '🎃'.encode(ENCODING)

INT_LENGTH = 4
SYMBOL_LENGTH = 2
