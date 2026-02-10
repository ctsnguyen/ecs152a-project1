
with open("docker/file.mp3", "rb") as f:
        mp3_bytes = f.read()
        mp3_size = len(mp3_bytes)
        

print(len(mp3_bytes))