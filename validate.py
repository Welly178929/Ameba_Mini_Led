import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.voice_controller import parse_voice_command

print(parse_voice_command('左邊開燈'))
print(parse_voice_command('右邊開燈'))
print(parse_voice_command('今天天氣很好'))
print(parse_voice_command('左邊關燈'))
