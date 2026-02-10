DATA = []

with open("docker/file.mp3", "rb") as f:
        mp3_bytes = f.read()
        mp3_size = len(mp3_bytes)
        
for i in range(mp3_size):
        DATA.append(mp3_bytes[i])

print(DATA)

print(type(DATA[12]))
