# How to run the code
All the Python Sender implementation is imported to client.py
In order to run everything you can run it all individual or
```
python3 client.py
```
or
```
python client.py
```

You can also use command line arguments to run the desired protocol
```
python3 client.py [tcp_reno | stop_and_go | fixed_slide_win]
```
* You could also just run the files itself if it's easier

If you decide to use client.py and run it without any command line arguments
you will just run the protocol that currently has the true value for it's macro
* For example STOP_AND_GO = True by default so it will run that

## File checking
file_check.py checks if the input and output mp3 files
are the same.

We do this by checking if the lengths are the same, then checking
whether the individual items at each index are the same.

# Some issues we ran into
Depending on the wifi or the hardware sending the files using
stop_and_go.py takes pretty long. 

