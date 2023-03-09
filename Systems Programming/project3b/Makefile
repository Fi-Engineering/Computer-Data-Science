CC=gcc

all: tcpclient multi-tcpserver

# compile part a
tcpclient : tcpclient.c
	$(CC) -o tcpclient tcpclient.c

multi-tcpserver : multi-tcpserver.c
	$(CC) -o multi-tcpserver multi-tcpserver.c -pthread

# TODO: compile part b. check the project write-up for commands

# TODO: compile part c

clean:
	rm tcpclient multi-tcpserver 
# TODO: may need to expand the line above