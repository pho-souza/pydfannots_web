import platform
__version__ = '0.1.1'
__platform__ = platform.system()
LINEBREAK = '\n'

if __platform__ == "Linux":
	LINEBREAK = '\n'
elif __platform__ == "Windows":
	LINEBREAK = '\r\n'
elif __platform__ == "Darwin":
	LINEBREAK = '\r'
else:
	LINEBREAK = '\n'