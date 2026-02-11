
with open("docker/file.mp3", "rb") as f:
        mp3_bytes_orig = f.read()
        
        
with open("docker/hdd/file2.mp3", "rb") as f:
        mp3_bytes_new = f.read()

if len(mp3_bytes_orig) == len(mp3_bytes_orig):
    print("Both files are the same length!")

i = 0
print("Checking if files match...")
files_match = True
while i < len(mp3_bytes_orig) and i < len(mp3_bytes_new):
    
    if mp3_bytes_orig[i] != mp3_bytes_new[i]:
        print(f"File don't match at index {i}!!!!")
        files_match = False
        continue
    i += 1

print("File Check Done!")
if files_match:
    print("It's a match!!!")
else:
    print("Files Don't Match :(")
