#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <assert.h>
#include <fcntl.h>

#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

/* This is a reference socket server implementation that prints out the messages
 * received from clients. */

#define MAX_PENDING 100
#define MAX_LINE 20

typedef struct client {
	int initSeq;
	int fd;
} client;


client* initClient(int initSeq, int fd) {
	client* clt = (client*) malloc(sizeof(client));
	assert(clt != NULL);
	clt->initSeq = initSeq;
	clt->fd = fd;
	return clt;
}

void freeClient(client* clt) {
	assert(clt != NULL);
	free(clt);
}

client* initClient(int initSeq, int fd);
void freeClient(client* clt);
char* get_return_message(int* x, char* buf, int len);
int handle_first_shake(client* clt);
void handle_second_shake(client* clt);

int main(int argc, char *argv[]) {
	char* host_addr = "127.0.0.1";
	int port = atoi(argv[1]);

	/*setup passive open*/
	int s;
	if ((s = socket(PF_INET, SOCK_STREAM, 0)) <0) {
		perror("simplex-talk: socket");
		exit(1);
	}

	/* Config the server address */
	struct sockaddr_in sin;
	sin.sin_family = AF_INET; 
	sin.sin_addr.s_addr = inet_addr(host_addr);
	sin.sin_port = htons(port);
	// Set all bits of the padding field to 0
	memset(sin.sin_zero, '\0', sizeof(sin.sin_zero));

	/* Bind the socket to the address */
	if ((bind(s, (struct sockaddr*)&sin, sizeof(sin)))<0) {
		perror("simplex-talk: bind");
		exit(1);
	}

	// connections can be pending if many concurrent client requests
	listen(s, MAX_PENDING);
	socklen_t len = sizeof(sin);
	
	// client state array
	client* clients[MAX_PENDING];
	for (int i=0; i<MAX_PENDING; i++) {
		client* nullClient = initClient(-1, -1);
		clients[i] = nullClient;
	}
	int numClients = 0;

	struct timeval tv;
	// 50 ms
	tv.tv_sec = 0;
	tv.tv_usec = 50000;

	fd_set master;
	FD_ZERO(&master);
	// set server socket to non-blocking
	fcntl(s, F_SETFL, O_NONBLOCK);
	// add to master set
	FD_SET(s, &master);

	while (1) {
		fd_set readfds;
		// copy master set into readfds
		readfds = master;

		int max_fd = 0;
		for(int i = 0; i < MAX_PENDING; i++)
			if(clients[i]->fd > max_fd)
				max_fd = clients[i]->fd;

		if (max_fd == 0)
			max_fd = s;

		// try to accept a new connection on server socket
		int currentFD;

		// see if server/clients are ready for communication
		int status = select(max_fd+1, &readfds, NULL, NULL, &tv);
		if(status < 0) {
			perror("pselect");
			exit(1);
		}
		// if the number of bits in the ready bits set is 0,
		// then status is 0 and no communication is occurring
		else if (status == 0) {
			continue;
		}
		// server socket is ready, meaning ?
		int contWhile = 0;
		if (FD_ISSET(s, &readfds)) {
			// printf("socket ready for new connection\n");
			currentFD = accept(s, (struct sockaddr *)&sin, &len);
			// there's a new connection since s is set
			// puts("client connected");
			client* newClient = initClient(-1, currentFD);
			clients[numClients] = newClient;
			numClients++;
			fcntl(currentFD, F_SETFL, O_NONBLOCK);
			FD_SET(currentFD, &master);
		} else {
			for (int i=0; i<max_fd+1; i++) {
				if (!FD_ISSET(i, &readfds)) {
					continue;
				}
				// printf("fd %d ready!\n", i);
				currentFD = i;
				for (int j=0; j<MAX_PENDING; j++) {
					// if we've already seen this fd
					if (currentFD == clients[j]->fd) {
						// if there's no sequence number assigned
						if (clients[j]->initSeq == -1) {
							// handle first handshake
							// printf("first handshake with %d\n", currentFD);
							int errCode = handle_first_shake(clients[j]);
							if (errCode == -1) {
								freeClient(clients[j]);
								client* nullClient = initClient(-1, -1);
								clients[j] = nullClient;
								FD_CLR(currentFD, &master);
							}
						} else {
							// handle second shake
							// printf("second handshake with %d, initSeq is %d\n", currentFD, clients[j]->initSeq);
							handle_second_shake(clients[j]);
							freeClient(clients[j]);
							client* nullClient = initClient(-1, -1);
							clients[j] = nullClient;
							FD_CLR(currentFD, &master);
						}
					} 
				}
			}
		}
	}
	for (int i=0; i<MAX_PENDING; i++) {
		freeClient(clients[i]);
	}
	return 0;
}

char* get_return_message(int* x, char* buf, int len) {
	const char msg[7] = "HELLO ";
	char* error = "ERROR";
	int i;
	// strlen is 6
	for (i=0; i<strlen(msg); i++) {
		if (buf[i] != msg[i]) {
			printf("ERROR: mismatch char at pos %d in %s\n", i, buf);
			return error;
		}
	}
	// printf("message is fine\n");
	// i is 6
	char xStr[MAX_LINE];
	int j;
	for (j=0; i<len; i++) {
		// printf("i: %d\nchar: %c\n", i, buf[i]);
		if (buf[i] >= '0' && buf[i] <= '9') {
			xStr[j] = buf[i];
			j++;
		} else {
			printf("ERROR: invalid non-numeric char at pos %d in %s (%c)\n", i, buf, buf[i]);
			return error;
		}
	}
	// printf("message's initSeq is ok\n");
	xStr[j] = '\0';
	// printf("calling atoi\n");
	int num = atoi(xStr);
	*x = num;
	// printf("initSeq = %d\n", num);
	char* returnMessage = (char*) malloc(MAX_LINE);
	// printf("calling sprintf\n");
	sprintf(returnMessage, "%s%d", msg, num+1);
	// printf("returnMessage = %s\n", returnMessage);
	return returnMessage;
}

int handle_first_shake(client* clt) {
	//recv, send
	int new_s = clt->fd;

	// message buffer
	char* buf = (char*) malloc(MAX_LINE);
	memset(buf, 0, MAX_LINE);

	// printf("receiving msg from client %d\n", new_s);
	int len = recv(new_s, buf, MAX_LINE, 0);
	// printf("len = %d\n", len);
	if (len < 1) {
		printf("ERROR: invalid message from client %d", new_s);
		goto close;
	}
	int x = 0;
	// printf("'%s' received\n", buf);
	char* returnMessage = get_return_message(&x, buf, len);
	// if returnMessage is error
	if (strcmp(returnMessage, "ERROR") == 0) goto close;
	clt->initSeq = x;
	// print message from client to console
	puts(buf);

	// printf("sending y: '%s'\n", returnMessage);
	send(new_s, returnMessage, strlen(returnMessage), 0);
	// clear buffer
	free(buf);
	free(returnMessage);
	return 0;

	close:
		memset(buf, 0, MAX_LINE);
		free(returnMessage);
		free(buf);
		close(new_s);
		return -1;
}

void handle_second_shake(client* clt) {
	//verify new message with recv() and
	//ensure that it is 2 greater than last
	//recv, send
	int new_s = clt->fd;

	// message buffer
	char* buf = (char*) malloc(MAX_LINE);
	memset(buf, 0, MAX_LINE);

	int len = recv(new_s, buf, MAX_LINE, 0);
	if (len < 1) {
		printf("ERROR: invalid message from client %d", new_s);
		goto close;
	}
	int z = 0;
	char* returnMessage = get_return_message(&z, buf, len);
	if (strcmp(returnMessage, "ERROR") == 0) goto close;

	if (z != clt->initSeq + 2) {
		printf("ERROR: integer recvd from client %d != %d + 2", z, clt->initSeq);
		goto close;
	}

	// print message from client to console
	puts(buf);

	goto close;
	close:
		free(returnMessage);
		free(buf);
		close(new_s);
		return;
}