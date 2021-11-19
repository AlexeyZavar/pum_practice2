###################################
# PUM Practice configuration file #
###################################


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
SYMBOL_SEPARATOR = '\0'.encode(ENCODING)

INT_LENGTH = 4
SYMBOL_LENGTH = 2

CALLBACK_STEP = 80
