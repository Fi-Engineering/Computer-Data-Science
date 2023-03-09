CC=gcc

all: tcpclient async-tcpserver

# compile part a
tcpclient : tcpclient.c
	$(CC) -o tcpclient tcpclient.c

async-tcpserver : async-tcpserver.c
	$(CC) -o async-tcpserver async-tcpserver.c -pthread

# TODO: compile part b. check the project write-up for commands

# TODO: compile part c

clean:
	rm tcpclient async-tcpserver 
# TODO: may need to expand the line above