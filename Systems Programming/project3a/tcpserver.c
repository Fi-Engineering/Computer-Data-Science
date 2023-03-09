#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

/* This is a reference socket server implementation that prints out the messages
 * received from clients. */

#define MAX_PENDING 20
#define MAX_LINE 20

int main(int argc, char *argv[]) {
  char* host_addr = "127.0.0.1";
  int port = atoi(argv[1]);

  /*setup passive open*/
  int s;
  if((s = socket(PF_INET, SOCK_STREAM, 0)) <0) {
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
  if((bind(s, (struct sockaddr*)&sin, sizeof(sin)))<0) {
    perror("simplex-talk: bind");
    exit(1);
  }

  // connections can be pending if many concurrent client requests
  listen(s, MAX_PENDING); 

  /* wait for connection, then receive and print text */
  int new_s; //file descriptor for socket
  socklen_t len = sizeof(sin);
  char buf[MAX_LINE];
  memset(buf, 0, MAX_LINE);
  while(1) {
    // puts("awaiting connection");
    if((new_s = accept(s, (struct sockaddr *)&sin, &len)) <0){
      perror("simplex-talk: accept");
      exit(1);
    }
    // puts("client connected");
    int numShake = 0;
    int lastNum = 0;
    // printf("buf: '%s'\n", buf);
    while(len = recv(new_s, buf, sizeof(buf), MSG_WAITALL)) {
      printf("received '%s' of size %d\n", buf, len);
      numShake++;
      char returnMessage[MAX_LINE];
      const char msg[7] = "HELLO ";
      int i;
      // strlen is 6
      for (i=0; i<strlen(msg); i++) {
        if (buf[i] != msg[i]) {
          printf("ERROR: mismatch char at pos %d in %s\n", i, buf);
          goto close;
        }
      }
      //i is 6
      char xStr[MAX_LINE];
      int j;
      for (j=0; i<len; i++) {
        // printf("i: %d\nchar: %c\n", i, buf[i]);
        if (buf[i] >= '0' && buf[i] <= '9') {
          xStr[j] = buf[i];
          j++;
        } else {
          printf("ERROR: invalid non-numeric char at pos %d in %s (%c)\n", i, buf, buf[i]);
          goto close;
        }
      }
      xStr[j] = '\0';
      int x = atoi(xStr);
      // if we already set lastNum, make sure x is lastNum + 1
      // printf("x: %d\nlastNum: %d\n", x, lastNum);
      if (numShake != 1 && x != lastNum + 1) {
        puts("ERROR: message received is not last message + 1");
        goto close;
      }
      lastNum = x + 1;
      sprintf(returnMessage, "%s%d", msg, x+1);
      // printf("%d\n", len);
      switch (numShake) {
        case 1:
          for (int k=0; k<len; k++) {
            printf("%c", buf[k]);
          }
          puts("");
          printf("sending y: '%s'\n", returnMessage);
          write(new_s, returnMessage, strlen(returnMessage));
          break;
        case 2:
          for (int k=0; k<len; k++) {
            printf("%c", buf[k]);
          }
          puts("");
          goto close;
          break;
      }
      // clear buffer
      memset(buf, 0, MAX_LINE);
    }
    close:
      memset(buf, 0, MAX_LINE);
      close(new_s);
      // puts("connection closed");
  }

  return 0;
}