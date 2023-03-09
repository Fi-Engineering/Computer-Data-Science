#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "tokenizer.h"

pid_t childPid = 0;

void executeShell();

TOKENIZER* getInput();

int checkDirection(char** lastDirection, char** direction);

int getNumSpaces (char** command, char** pos, char** back);

int runCommand(char* command, int file, int output);

void writeToStdout(char *text);

void killChildProcess();

void sigintHandler(int sig);

void registerSignalHandlers();

/**
 * Main program execution
 */
int main( int argc, char *argv[] )
{
  registerSignalHandlers();

  while (1) {
    executeShell();
  }

  return 0;			/* all's well that end's well */
}

void executeShell() {

  char minishell[] = "penn-sh# ";
  writeToStdout(minishell);

  TOKENIZER *tokenizer;
  tokenizer = getInput();
  if (tokenizer == NULL) {
    printf("%s\n", "Exiting...");
    exit(EXIT_SUCCESS);
  }
  if (*tokenizer->str == '\0') return;

  char *tok1 = (char*) malloc(256);
  char *tok2;
  char *tok3;
  char *dest;
  char *direction = (char*) malloc(2);
  direction[1] = '\0';
  direction[1] = '\0';
  char *lastDirection = (char*) malloc(2);
  lastDirection[0] = '\0';
  lastDirection[1] = '\0';
  int file = -1;
  int output = -1;
  int errCode = 0;

  while (1) {
    // reset childPid just in case of abnormal closing prior
    childPid = 0;

    // get first token and direction if applicable
    char* tok = get_next_token(tokenizer);
    if (tok == NULL && file == -1 && output == -1) {
      printf("%s\n", "Invalid: command not found");
      break;
    } else if (tok == NULL) {
      printf("%s\n", "Invalid: no command provided");
      break;
    }
    strcpy(tok1, tok);
    free(tok);
    // printf("tok1: %s\n", tok1);

    char* space = (char*) malloc(2);
    space[0] = ' ';
    space[1] = '\0';
    char* temp;
    temp = get_next_token(tokenizer);
    if (temp == NULL) {
      if (runCommand(tok1, -1, -1) == -1) {
        printf("%s\n", "Invalid: program failed or command not found");
        break;
      }
      break;
    }
    // printf("%c\n", *temp);
    *direction = *temp;
    // printf("dir: %s\n", direction);
    while ((errCode = checkDirection(&space, &temp)) != 0) {
      space[0] = ' ';
      // temp has reached end of line if NULL
      if (temp == NULL) {
        if (runCommand(tok1, -1, -1) == -1) {
          printf("%s\n", "Invalid: program failed or command not found");
          goto cleanup;
        }
        goto cleanup;
      }
      // printf("temp: %s\n", temp);
      strcat(tok1, space);
      strcat(tok1, temp);
      // printf("tok1: %s\n", tok1);
      // direction should be the first char of temp since
      // the previous while loop broke on that condition
      *direction = *temp;
      // printf("dir: %s\n", direction);
      free(temp);
      temp = get_next_token(tokenizer);
    }
    if (errCode == 0) {
      *direction = *temp;
      // printf("dir: %s\n", direction);
    }
    free(space);
    // essentially sets lastDirection to direction
    if (checkDirection(&lastDirection, &direction) != 0) {
      // direction is NULL or invalid, printed by checkDir
      close(file);
      close(output);
      break;
    }
    // printf("dir: %s\n", direction);
    // printf("lastDir: %s\n", lastDirection);

    // get token after first direction
    tok2 = get_next_token(tokenizer);
    if (tok2 == NULL) {
      printf("%s\n", "Invalid: no token found after directional delimiter");
      close(file);
      close(output);
      break;
    }

    // figure out direction
    // if right, then just run program and copy to file,
    // unless there's a third token, in which case we need to
    // use that token as input to tok1
    if (strcmp(">", direction) == 0) {
      output = open(tok2, O_WRONLY | O_TRUNC | O_CREAT, 0644);
      if (output == -1) {
        printf("%s\n", "Invalid: second token file not found");
        break;
      }
      // checking for second direction
      direction = get_next_token(tokenizer);
      // printf("second dir: %s\n", direction);
      // just run command to stdout if no second direction
      if (checkDirection(&lastDirection, &direction) != 0) {
        if (runCommand(tok1, -1, output) == -1) {
          printf("%s\n", "Invalid: program failed or command not found");
          close(output);
          break;
        }
        // printf("%s\n", "checkDirection returned not 0");
        break;
      } else {
        // otherwise use third token as input
        tok3 = get_next_token(tokenizer);
        if (tok3 == NULL) {
          printf("%s\n", "Invalid: no token found after directional delimiter");
          close(output);
          break;
        }
        // shouldn't have more than 3 non-directional tokens
        if (get_next_token(tokenizer) != NULL) {
          printf("%s\n", "Invalid: Multiple standard input redirects or redirect in invalid location");
          break;
        }
        file = open(tok3, O_RDONLY, 0644);
        if (runCommand(tok1, file, output) == -1) {
          printf("%s\n", "Invalid: program failed or command not found");
          close(output);
          break;
        }
        break;
      }
    } else if (strcmp("<", direction) == 0) {
      // take tok2 as file input for tok1
      file = open(tok2, O_RDONLY, 0644);
      // next token (second direction) needs to be a '>'
      // (if it exists)
      direction = get_next_token(tokenizer);
      if (checkDirection(&lastDirection, &direction) != 0) {
        // just print to stdout
        // printf("%s\n", "no second dir found, printing output to stdout");
        if (runCommand(tok1, file, -1) != 0) {
          printf("%s\n", "Invalid: program failed or command not found");
          break;
        }
        break;
      }
      // printf("second dir: %s\n", direction);
      // define output to be third token
      tok3 = get_next_token(tokenizer);
      output = open(tok3, O_WRONLY | O_TRUNC | O_CREAT, 0644);
      free(tok3);
      if (file == -1) {
        printf("%s\n", "Invalid: no such file or directory");
        break;
      }
      // shouldn't have more than 3 non-directional tokens
      if (get_next_token(tokenizer) != NULL) {
        printf("%s\n", "Invalid: Multiple standard input redirects or redirect in invalid location");
        break;
      }
      if (runCommand(tok1, file, output) != 0) {
        printf("%s\n", "Invalid: program failed or command not found");
        break;
      }
      break;
    }
  }
cleanup:
  close(file);
  close(output);
  free(tok1);
  free(tok2);
  free(direction);
  free(lastDirection);
  free_tokenizer(tokenizer); /* free memory */
}

TOKENIZER* getInput() {
  TOKENIZER *tokenizer;
  int br;
  char string[256] = "";
  string[255] = '\0';    /* ensure that string is always null-terminated */
  while ((br = read( STDIN_FILENO, string, 255 )) > 0) {
    if (br <= 0) {
      // printf("%s (%d)\n", "less than or equal to 1", br);
      return NULL;
    }
    string[br-1] = '\0';   /* remove trailing \n */
    /* tokenize string */
    tokenizer = init_tokenizer( string );
    return tokenizer;
  }
  tokenizer = NULL;
  return tokenizer;
}

int checkDirection(char** lastDirection, char** direction) {
   // printf("checking lastDir: %s\n", *lastDirection);
   // printf("checking dir: %s\n", *direction);
  if (*direction == NULL || *lastDirection == NULL) {
    // printf("%s\n", "pointers empty");
    return 1;
  } else if (**direction == **lastDirection) {
    printf("%s\n", "Invalid: Multiple standard input redirects or redirect in invalid location");
    return -1;
  } else if (**direction != '<' && **direction != '>') {
    if (!isspace(**lastDirection)) {
      printf("%s (%s)\n", "Invalid: direction symbol invalid", *direction);
    }
    return -1;
  }
  // printf("%s\n", "valid directions");
  **lastDirection = **direction;
  // printf("%s\n", "problem..?");
  return 0;
}

int runCommand(char* command, int file, int output) {
  char* pos = command;
  // to ignore trailing whitespaces start at end character
  char* back = command + strlen(command) - 1;
  // loop through command counting relevant argument spaces
  int spaces = 0;
  // ignore leading whitespaces
  while (isspace(*pos)) pos++;
  // printf( "First non-space char = '%c'\n", *pos );
  while (isspace(*back)) back--;
  // adjust back to point to first irrelevant space
  back++;
  // printf( "Last non-space char = '%c'\n", *(back-1) );
  while (*pos != '\0' && pos != back) {
    if (isspace(*pos)) {
      //printf( "Space found\n" );
      spaces++;
    }
    pos++;
  }
  // printf( "spaces: '%d'\n", spaces );
  //+2 because of null termination and the fact that there is one more argument than spaces
  char *args[spaces+2];

  // include first token in args
  // make char *args[spaces+2]
  // populate args with arguments

  // redefine these for argument population
  pos = command;
  while (isspace(*pos)) pos++;

  int numArgs = 0;
  while (*(pos) != '\0' && pos != back) {
    if isspace(*pos) {
      pos++;
      continue;
    }
    char* str = (char *)malloc(256);
    str[255] = '\0';
    int strPos = 0; 
    while (!isspace(*pos) && strPos != 255 && *pos != '\0') {
      str[strPos] = *pos;
      strPos++;
      pos++;
    }
    str[strPos] = '\0';
    // printf("%s\n", str);
    args[numArgs] = str;
    numArgs++;
    // numArgs should not be larger than spaces + 2 because
    // spaces + 1 are the actual num of args and the last arg
    // must be null
    if (numArgs == spaces + 2) {
      printf("%s\n", "Invalid: arguments spaced incorrectly");
      return -1;
    }
  }

  // printf( "numArgs: %d\n", numArgs );
  // terminate with NULL
  args[numArgs] = NULL;
  // printf( "args[0]: '%s'\n", args[0] );
  
  // run program
  int status;
  childPid = fork();

  if (childPid < 0) {
    perror("Invalid: Error in creating child process");
    return -1;
  }

  if (childPid == 0) {
    // child
    // read in from file 
    int stdinCopy = dup(STDIN_FILENO);
    if (file != -1) {
      if (dup2(file, STDIN_FILENO) == -1) {
        perror("Invalid: Error in changing file descriptor");
        return -1;
      }
    }
    int stdoutCopy = dup(STDOUT_FILENO);
    if (output != -1) {
      if (dup2(output, STDOUT_FILENO) == -1) {
        perror("Invalid: Error in changing file descriptor");
        return -1;
      }
    }
    if (execvp(args[0], args) == -1) {
      // un dup
      if (dup2(stdinCopy, STDIN_FILENO) == -1 || dup2(stdoutCopy, STDOUT_FILENO) == -1) {
        perror("Invalid: Error in changing file descriptors");
        return -1;
      }
      close(stdinCopy);
      close(stdoutCopy);
      perror("Invalid: Error in execvp");
      output = -1;
      return -1;
    }
    if (dup2(stdinCopy, STDIN_FILENO) == -1 || dup2(stdoutCopy, STDOUT_FILENO) == -1) {
      perror("Invalid: Error in changing file descriptors");
      return -1;
    }
    close(stdinCopy);
    close(stdoutCopy);
  } else {
    // parent
    do {
        if (wait(&status) == -1) {
            perror("Error in child process termination");
            exit(EXIT_FAILURE);
            return -1;
        }
    } while (!WIFEXITED(status) && !WIFSIGNALED(status));
    // reset childPid
    childPid = 0;
  }
  for (int i=0; i<numArgs; i++) {
    free(args[i]);
  }
  return 0;
}

void writeToStdout(char *text) {
  if (write(STDOUT_FILENO, text, strlen(text)) == -1) {
      perror("Error in write");
      exit(EXIT_FAILURE);
  }
}

/* Sends SIGKILL signal to a child process.
 * Error checks for kill system call failure and exits program if
 * there is an error */
void killChildProcess() {
  writeToStdout("\n");
  if (kill(childPid, SIGKILL) == -1) {
    perror("Error in kill");
    exit(EXIT_FAILURE);
  }
  childPid = 0;
}

/* Signal handler for SIGINT. Catches SIGINT signal (e.g. Ctrl + C) and
 * kills the child process if it exists and is executing. Does not
 * do anything to the parent process and its execution */
void sigintHandler(int sig) {
  if (childPid != 0) {
    killChildProcess();
  }
}

void registerSignalHandlers() {
  if (signal(SIGINT, sigintHandler) == SIG_ERR) {
      perror("Error in signal");
      exit(EXIT_FAILURE);
  }
}
/*
// direction 0 = left
// direction 1 = right
int assertAndMove(fileA, fileB, outputA, outputB, int direction) {
  // if fileA is not -1, fileA is a file
  // if fileB is not -1, fileB is a file
  // if fileA and fileB are files, file to file redirection?
  // if outputA is not -1, outputA is program output
  // if outputB is not -1, outputB is program output
  // if outputA and outputB are programs outputs, output to output redirection?
  if (direction == 0) {
    // left

  } else if (direction == 1) {
    // right

  } else {
    // invalid
  }
}*/