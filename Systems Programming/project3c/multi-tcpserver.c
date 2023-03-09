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

		// try to accept a new connection on server socket
		int currentFD;
		currentFD = accept(s, (struct sockaddr *)&sin, &len);

		// see if server/clients are ready for communication
		int status = select(s, &readfds, NULL, NULL, &tv);

		if(status < 0) {
			perror("pselect");
			exit(1);
		}
		// if the number of bits in the ready bits set is 0,
		// then status is 0 and no communication is occurring
		else if (status == 0)
			continue;
		// server socket is ready, meaning ?
		int contWhile = 0;
		if (FD_ISSET(s, &readfds)) {
			for (int i=0; i<MAX_PENDING; i++) {
				// if we've already seen this fd
				if (currentFD == clients[i]->fd) {
					// if there's no sequence number assigned
					if (clients[i]->initSeq != -1) {
						// handle first handshake
						printf("first handshake with %d\n", currentFD);
						int errCode = handle_first_shake(clients[i]);
						if (errCode == -1) {
							freeClient(clients[i]);
							client* nullClient = initClient(-1, -1);
							clients[i] = nullClient;
						}
						contWhile = 1;
						break;
					} else {
						// handle second shake
						printf("second handshake with %d\n", currentFD);
						handle_second_shake(clients[i]);
						freeClient(clients[i]);
						client* nullClient = initClient(-1, -1);
						clients[i] = nullClient;
						contWhile = 1;
						break;
					}
				}
			}
			if (contWhile) continue;
			// if we've made it here, there's a new connection
			// since there is no client with currentFD as its fd
			puts("client connected");
			client* newClient = initClient(-1, currentFD);
			clients[numClients] = newClient;
			numClients++;
			fcntl(currentFD, F_SETFL, O_NONBLOCK);
			FD_SET(currentFD, &master);
		}
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
	xStr[j] = '\0';
	int num = atoi(xStr);
	*x = num;
	char* returnMessage;
	sprintf(returnMessage, "%s%d", msg, num+1);
	if (strlen(returnMessage) > MAX_LINE) return error;
	return returnMessage;
}

int handle_first_shake(client* clt) {
	//recv, send
	int new_s = clt->fd;

	// message buffer
	char buf[MAX_LINE];
	memset(buf, 0, MAX_LINE);

	int len = recv(new_s, buf, sizeof(buf), 0);
	if (len < 1) {
		printf("ERROR: invalid message from client with fd = %d", new_s);
		goto close;
	}
	int x = 0;
	char* returnMessage = get_return_message(&x, &buf, len);
	// if returnMessage is error
	if (strcmp(returnMessage, "ERROR") == 0) goto close;
	clt->initSeq = x;

	// print message from client to console
	for (int k=0; k<len; k++) {
		printf("%c", buf[k]);
	}
	puts("");

	// printf("sending y: '%s'\n", returnMessage);
	send(new_s, returnMessage, strlen(returnMessage), 0);
	// clear buffer
	memset(buf, 0, MAX_LINE);
	return 0;

	close:
		memset(buf, 0, MAX_LINE);
		close(new_s);
		return -1;
}

void handle_second_shake(client* clt) {
	//verify new message with recv() and
	//ensure that it is 2 greater than last
	//recv, send
	int new_s = clt->fd;

	// message buffer
	char buf[MAX_LINE];
	memset(buf, 0, MAX_LINE);

	int len = recv(new_s, buf, sizeof(buf), 0);
	if (len < 1) {
		printf("ERROR: invalid message from client with fd = %d", new_s);
		goto close;
	}
	int z = 0;
	char* returnMessage = get_return_message(&z, &buf, len);
	if (strcmp(returnMessage, "ERROR") == 0) goto close;

	if (z != clt->initSeq + 2) {
		printf("ERROR: integer recvd from client (%d) != %d + 2", z, clt->initSeq);
		goto close;
	}

	// print message from client to console
	for (int k=0; k<len; k++) {
		printf("%c", buf[k]);
	}
	puts("");

	goto close;
	close:
		memset(buf, 0, MAX_LINE);
		close(new_s);
		return;
}