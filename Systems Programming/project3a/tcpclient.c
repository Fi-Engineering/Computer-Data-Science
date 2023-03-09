#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/socket.h>
#include <netinet/ip.h>
#include <arpa/inet.h>

#define MAX_LINE 20

int main (int argc, char *argv[]) {
  char* host_addr = argv[1];
  int port = atoi(argv[2]);
  int initSeq = atoi(argv[3]);
  // printf("initSeq: %d\n", initSeq);

  /* Open a socket */
  int s;
  if((s = socket(PF_INET, SOCK_STREAM, 0)) <0){
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

  /* Connect to the server */
  if(connect(s, (struct sockaddr *)&sin, sizeof(sin))<0){
    perror("simplex-talk: connect");
    close(s);
    exit(1);
  }
  // puts("connected to server");

  const char msg[7] = "HELLO ";
  char buf[MAX_LINE];
  memset(buf, 0, MAX_LINE);
  int len = sprintf(buf, "%s%d", msg, initSeq);
  buf[len] = '\0';
  // printf("buf: %s\nlen: %d\n",buf,len);
  /*for (int k=0; k<strlen(buf); k++) {
    printf("%c\n", buf[k]);
  }*/
  printf("sending x: '%s' of size %d\n", buf, len);
  printf("send result: %d\n", send(s, buf, len, 0));

  // clear buffer and get next message using it
  memset(buf, 0, MAX_LINE);
  len = recv(s, buf, sizeof(buf), 0);
  // print message from server (HELLO Y)
  puts(buf);

  // verify that hello y from server is x+1
  int i;
  // strlen is 6
  for (i=0; i<strlen(msg); i++) {
    if (buf[i] != msg[i]) {
      printf("ERROR: mismatch char at pos %d in %s\n", i, buf);
      return -1;
    }
  }
  //i is 6
  char yStr[MAX_LINE];
  int j;
  for (j = 0; i < strlen(buf); i++) {
    if (buf[i] >= '0' && buf[i] <= '9') {
      yStr[j] = buf[i];
      j++;
    } else {
      printf("ERROR: invalid non-numeric char at pos %d in %s (%c)\n", i, buf, buf[i]);
      return -1;
    }
  }
  yStr[j] = '\0';
  int y = atoi(yStr);

  if (y != initSeq + 1) {
    puts("ERROR: y is not equal to initSeq + 1");
    return -1;
  }
  // clear buffer
  memset(buf, 0, MAX_LINE);
  sprintf(buf, "%s%d", msg, y+1);
  // printf("sending z: %s\n", buf);
  // send z
  send(s, buf, strlen(buf), 0);

  return 0;
}
