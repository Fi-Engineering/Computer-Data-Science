#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <assert.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "tokenizer.h"

#ifndef __PARAMS_H__
#define __PARAMS_H__

typedef struct params {
  char *command;
  int input; // file descriptor for input
  int output; // file descriptor for output
  TOKENIZER* tokenizer;
} PARAMS;

/**
 * Initializes the params class
 *
 * @param command the string that will be tokenized.  Should be non-NULL.
 * @param input the file descriptor for the input
 * @param output the file descriptor for the output
 * @return an initialized params class on success, NULL on error.
 */
PARAMS *init_params(TOKENIZER* tokenizer, char *command, int input, int output);

/**
 * Deallocates space used by the params class.
 * @param params a non-NULL, initialized params class
 */
void free_params( PARAMS *params );
#endif


pid_t childPid = 0;

void executeShell();

PARAMS* getProgramParameters(TOKENIZER* tokenizer);

TOKENIZER* getInput();

int checkDirection(char** lastDirection, char** direction);

int getNumSpaces (char** command, char** pos, char** back);

int runCommand(char* command, int file, int output, int std);

void writeToStdout(char *text);

void killChildProcess();

void sigintHandler(int sig);

void registerSignalHandlers();

/**
 * Main program execution
 */
int main(int argc, char *argv[]) {
  registerSignalHandlers();

  while (1) {
    executeShell();
  }

  return 0;      /* all's well that end's well */
}

PARAMS *init_params(TOKENIZER* tokenizer, char *command, int input, int output) {
  PARAMS *params;
  int len;
  assert(command != NULL);

  params = (PARAMS *) malloc(sizeof(PARAMS));
  assert(params != NULL);
  len = strlen(command) + 1; /* don't forget \0 char */
  params->command = (char *) malloc(len);
  assert(params->command != NULL);
  memcpy(params->command, command, len);
  params->input = input;
  params->output = output;
  params->tokenizer = tokenizer;
  return params;
}

void free_params(PARAMS *params) {
  assert(params != NULL);
  free(params->command);
  free(params);
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

  // when reading the first params,
  // no output is allowed if pipe
  PARAMS* firstParams;
  PARAMS* secondParams;
  firstParams = getProgramParameters(tokenizer);
  if (firstParams == NULL) {
    // writeToStdout("first params null\n");
    return;
  }
  /*printf("%s\n", "first params");
  printf("  %s\n", firstParams->command);
  printf("  %d\n", firstParams->input);
  printf("  %d\n", firstParams->output);*/
  if (firstParams->tokenizer != NULL) {
    secondParams = getProgramParameters(firstParams->tokenizer);
    if (secondParams != NULL) {
      /*printf("%s\n", "second params");
      printf("  %s\n", secondParams->command);
      printf("  %d\n", secondParams->input);
      printf("  %d\n", secondParams->output);*/

      // at this point secondParams' tokenizer must be null because we only take one pipe
      if (secondParams->tokenizer != NULL) {
        printf("%s\n", "Invalid: multiple pipes");
        return;
      }
      if (secondParams->input != -1) {
        printf("%s\n", "Invalid: multiple inputs");
        return;
      }
      // create pipe, fork, etc.
      int fd[2], status;
      pid_t child_a, child_b;
      // char firstOutput[1024];

      if (pipe(fd) < 0) {
        printf("%s\n", "Invalid: pipe error");
        return;
      }
      if ((child_a = fork()) < 0) {
        printf("%s\n", "Invalid: fork error");
        return;
      } else if (child_a == 0) {
        // child_a
        // connecting write end (1) to stdout
        int stdoutCopy = dup(STDOUT_FILENO);
        //printf("stdoutCopy (child_a): %d\n", stdoutCopy);
        if (dup2(fd[1], STDOUT_FILENO) == -1) {
          perror("Invalid: Error in duping output to pipe write");
          exit(EXIT_FAILURE);
        }
        // close read end (0)
        close(fd[0]);
        printf("%s\n", "running first process");
        if (runCommand(firstParams->command, firstParams->input, -1, stdoutCopy) != 0) {
          perror("Invalid: first program execution failed");
          // dup2(stdoutCopy, STDOUT_FILENO);
          close(stdoutCopy);
          exit(EXIT_FAILURE);
        }
        /*if (dup2(stdoutCopy, STDOUT_FILENO) == -1) {
          perror("Invalid: Error in restoring STDOUT");
          exit(EXIT_FAILURE);
        }*/
        close(stdoutCopy);
        exit(EXIT_SUCCESS);
      } else {
        // parent
        child_b = fork();
        if (child_b < 0) {
          printf("%s\n", "Invalid: fork error");
          return;
        } else if (child_b == 0) {
          // child_b
          // connect read end (0) to stdin
          int stdinCopy = dup(STDIN_FILENO);
          // printf("stdinCopy (child_b): %d\n", stdinCopy);
          if (dup2(fd[0], STDIN_FILENO) == -1) {
            perror("Invalid: Error in duping input to pipe read");
            exit(EXIT_FAILURE);
          }
          // close write end (1)
          close(fd[1]);
          printf("%s\n", "running second process");
          if (runCommand(secondParams->command, -1, secondParams->output, stdinCopy) != 0) {
            perror("Invalid: second program execution failed");
            // dup2(stdinCopy, STDIN_FILENO);
            close(stdinCopy);
            exit(EXIT_FAILURE);
          }
          /*if (dup2(stdinCopy, STDIN_FILENO) == -1) {
            perror("Invalid: Error in restoring STDIN");
            exit(EXIT_FAILURE);
          }*/
          close(stdinCopy);
          exit(EXIT_SUCCESS);
        } else {
          // back to parent
          do {
            if (wait(&status) == -1) {
              perror("Invalid: error in child process termination");
              exit(EXIT_FAILURE);
              return;
            }
          } while (!WIFEXITED(status) && !WIFSIGNALED(status));
          waitpid(child_a, &status, 0);
          waitpid(child_b, &status, 0);
        }
      }
      free_params(firstParams);
      free_params(secondParams);
      return;
    } else {
      // printf("%s\n", "no second params");
    }
  } else {
    // writeToStdout("tokenizer null for firstParams, no second params\n");

    if (runCommand(firstParams->command, firstParams->input, firstParams->output, -1) != 0) {
      // don't need this print because runCommand reports itself
      // printf("%s\n", "Invalid: error in runCommand");
    }
    free_params(firstParams);
    return;
  }
  // when reading the second params,
  // no input is allowed
  free_tokenizer(tokenizer);
  free_params(firstParams);
}

PARAMS* getProgramParameters(TOKENIZER* tokenizer) {
  char *program = (char*) malloc(256);
  char *tok2 = NULL;
  char *tok3;
  char *dest;
  char *direction = (char*) malloc(2);
  direction[0] = '\0';
  direction[1] = '\0';
  char *lastDirection = (char*) malloc(2);
  lastDirection[0] = '\0';
  lastDirection[1] = '\0';
  int input = -1;
  int output = -1;
  int errCode = 0;

  // reset childPid just in case of abnormal closing prior
  childPid = 0;
  PARAMS* params = NULL;

  // get first token
  char* tok = get_next_token(tokenizer);
  if (tok == NULL && input == -1 && output == -1) {
    printf("%s\n", "Invalid: command not found");
    goto cleanup;
  } else if (tok == NULL) {
    printf("%s\n", "Invalid: no command provided");
    goto cleanup;
  }
  strcpy(program, tok);
  free(tok);
  // printf("program: %s\n", program);

  // gets first direction if applicable, else tacks on args to first token
  char* space = (char*) malloc(2);
  space[0] = ' ';
  space[1] = '\0';
  char* temp;
  temp = get_next_token(tokenizer);
  if (temp == NULL) {
    /*if (runCommand(program, -1, -1) == -1) {
      printf("%s\n", "Invalid: program failed or command not found");
      goto cleanup;
    }
    goto cleanup;*/

    // only 1 token present ('program')
    // printf("%s\n", "only 1 token found");
    params = init_params(NULL, program, -1, -1);
    goto cleanup;
  }
  // printf("%c\n", *temp);
  *direction = *temp;
  // printf("dir: %s\n", direction);
  while ((errCode = checkDirection(&space, &temp)) != 0) {
    // if errCode is 2, we have a pipe, so
    // pass the rest of the tokenizer along ('program |')
    if (errCode == 2) {
      // printf("%s\n", "pipe found");
      params = init_params(tokenizer, program, -1, -1);
      goto cleanup;
    }
    space[0] = ' ';
    // temp has reached end of line if NULL
    if (temp == NULL) {
      /* if (runCommand(program, -1, -1) == -1) {
        printf("%s\n", "Invalid: program failed or command not found");
        goto cleanup;
      }
      goto cleanup;*/
      // 'program args'
      // printf("%s\n", "format: program args");
      params = init_params(NULL, program, -1, -1);
      goto cleanup;
    }
    // printf("temp: %s\n", temp);
    strcat(program, space);
    strcat(program, temp);
    // printf("program: %s\n", program);
    // direction should be the first char of temp since
    // the previous while loop broke on that condition
    *direction = *temp;
    // printf("dir: %s\n", direction);
    free(temp);
    temp = get_next_token(tokenizer);
  }
  
  // temp is now the direction so update the appropriate pointer
  *direction = *temp;
  // printf("dir: %s\n", direction);
  free(space);
  // essentially sets lastDirection to direction
  if (checkDirection(&lastDirection, &direction) != 0) {
    // direction is NULL or invalid, printed by checkDir
    close(input);
    close(output);
    goto cleanup;
  }
  // printf("dir: %s\n", direction);
  // printf("lastDir: %s\n", lastDirection);

  // get token after first direction
  tok2 = get_next_token(tokenizer);
  if (tok2 == NULL) {
    printf("%s\n", "Invalid: no token found after directional delimiter");
    close(input);
    close(output);
    goto cleanup;
  }

  // figure out direction ('program (>/<) tok2')
  // if right, then just run program and copy to input,
  // unless there's a third token, in which case we need to
  // use that token as input to program
  if (strcmp(">", direction) == 0) {
    output = open(tok2, O_WRONLY | O_TRUNC | O_CREAT, 0644);
    if (output == -1) {
      printf("%s\n", "Invalid: second token input invalid");
      goto cleanup;
    } else {
      // printf("%s%d\n", "opened input for output with fd = ", output);
    }
    // checking for second direction
    direction = get_next_token(tokenizer);
    // printf("second dir: %s\n", direction);
    // just run command to stdout if no second direction
    if ((errCode = checkDirection(&lastDirection, &direction)) != 0) {
      // 'program > input |' construction, which is invalid
      if (errCode == 2) {
        printf("%s\n", "Invalid: output redirection nonsensical");
        goto cleanup;
      }
      /*if (runCommand(program, -1, output) == -1) {
        // printf("%s\n", "Invalid: program failed or command not found");
        close(output);
        goto cleanup;
      }*/
      // 'program > input'
      // printf("%s\n", "format: program > input");
      params = init_params(NULL, program, -1, output);
      goto cleanup;
    } else {
      // otherwise use third token as input ('program > input < tok3')
      // printf("%s\n", "checkDirection returned not 0");
      tok3 = get_next_token(tokenizer);
      if (tok3 == NULL) {
        printf("%s\n", "Invalid: no token found after directional delimiter");
        close(output);
        goto cleanup;
      }
      // shouldn't have more than 3 non-directional tokens
      if (get_next_token(tokenizer) != NULL) {
        printf("%s\n", "Invalid: excessive non-directional tokens");
        goto cleanup;
      }
      input = open(tok3, O_RDONLY, 0644);
      if (input == -1) {
        printf("%s\n", "Invalid: input selected for input not found");
        goto cleanup;
      }
      /*if (runCommand(program, input, output) == -1) {
        printf("%s\n", "Invalid: program failed or command not found");
        close(output); 
        goto cleanup;
      }*/
      params = init_params(NULL, program, input, output);
      goto cleanup;
    }
  } else if (strcmp("<", direction) == 0) {
    // take tok2 as input input for program ('program < input')
    input = open(tok2, O_RDONLY, 0644);
    if (input == -1) {
      printf("%s\n", "Invalid: input selected for input not found");
      goto cleanup;
    }
    // next token (second direction) needs to be a '>'
    // (if it exists)
    direction = get_next_token(tokenizer);
    if ((errCode = checkDirection(&lastDirection, &direction)) != 0) {
      // 'program < input |'
      if (errCode == 2) {
        // printf("%s\n", "pipe found");
        params = init_params(tokenizer, program, input, -1);
        goto cleanup;
      }
      // just print to stdout ('program < input')
      // printf("%s\n", "no second dir found, printing output to stdout");
      /*if (runCommand(program, input, -1) != 0) {
        // printf("%s\n", "Invalid: program failed or command not found");
        goto cleanup;
      }*/
      // printf("%s\n", "format: program < input");
      params = init_params(NULL, program, input, -1);
      goto cleanup;
    }
    // printf("second dir: %s\n", direction);
    // define output to be third token ('program < input > tok3')
    tok3 = get_next_token(tokenizer);
    output = open(tok3, O_WRONLY | O_TRUNC | O_CREAT, 0644);
    free(tok3);
    if (input == -1) {
      printf("%s\n", "Invalid: no such input or directory");
      goto cleanup;
    }
    // shouldn't have more than 3 non-directional tokens
    if (get_next_token(tokenizer) != NULL) {
      printf("%s\n", "Invalid: excessive non-directional tokens");
      goto cleanup;
    }
    /*if (runCommand(program, input, output) != 0) {
      printf("%s\n", "Invalid: program failed or command not found");
      goto cleanup;
    }*/
    // printf("%s\n", "format: program < input > output");
    params = init_params(NULL, program, input, output);
    goto cleanup;
  }
  cleanup:
    // writeToStdout("closing input, ");
    close(input);
    // writeToStdout("closing output ,");
    close(output);
    // writeToStdout("freeing program, ");
    free(program);
    // writeToStdout("freeing tok2, ");
    free(tok2);
    // writeToStdout("freeing direction, ");
    free(direction);
    // writeToStdout("freeing lastDirection\n");
    free(lastDirection);
    // writeToStdout("returning");
  return params;
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
  } else if (**direction == '|') {
    // printf("%s\n", "pipe found");
    return 2;
  }
  else if (**direction != '<' && **direction != '>') {
    if (!isspace(**lastDirection)) {
      printf("%s (%s)\n", "Invalid: direction symbol invalid", *direction);
    }
    return -1;
  }
  // printf("%s\n", "valid direction");
  **lastDirection = **direction;
  return 0;
}

int runCommand(char* command, int input, int output, int std) {
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
  // printf("%s\n", "running program");
  int status;
  childPid = fork();

  if (childPid < 0) {
    perror("Invalid: Error in creating child process");
    return -1;
  }

  if (childPid == 0) {
    // child
    // read in from input 
    // printf("%s\n", "test");
    //int stdinCopy = dup(STDIN_FILENO);
    //printf("stdinCopy: %d\n", stdinCopy);
    if (input != -1) {
      printf("input fd is %d, duping that to STDIN (%d)\n", input, STDIN_FILENO);
      if (std == -1) {
        if (dup2(input, STDIN_FILENO) != 0) {
          writeToStdout("Invalid: Error in duping input to STDIN\n");
          _exit(EXIT_FAILURE);
        }
      } else {
        printf("std: %d\n", std);
        if (dup2(input, std) == -1) {
          writeToStdout("Invalid: Error in duping input to std\n");
          _exit(EXIT_FAILURE);
        }
      }
    }
    // printf("%s\n", "test");
    //int stdoutCopy = dup(STDOUT_FILENO);
    //printf("stdoutCopy: %d\n", stdoutCopy);
    if (output != -1) {
      printf("output fd is %d, duping that to STDOUT (%d)\n", output, STDOUT_FILENO);
      if (std == -1) {
        if (dup2(output, STDOUT_FILENO) != 0) {
          writeToStdout("Invalid: Error in duping output to STDOUT\n");
          _exit(EXIT_FAILURE);
        }
      } else {
        printf("std: %d\n", std);
        if (dup2(output, std) != 0) {
          writeToStdout("Invalid: Error in duping output to std\n");
          _exit(EXIT_FAILURE);
        }
      }
    }
    // printf("%s\n", "test");
    if (execvp(args[0], args) != 0) {
      // un dup
      /*
      if (dup2(stdinCopy, STDIN_FILENO) == -1 || dup2(stdoutCopy, STDOUT_FILENO) == -1) {
        perror("Invalid: Error in restoring STDIN/STDOUT");
        return -1;
      }
      close(stdinCopy);
      close(stdoutCopy);*/
      // perror("Invalid: Error in execvp");
      // printf("%s\n", "test");
      writeToStdout("Invalid: command not found\n");
      output = -1;
      _exit(127); // command not found
    }
  } else {
    // parent
    do {
      if (wait(&status) == -1) {
        perror("Error in child process termination");
        exit(EXIT_FAILURE);
        return -1;
      } else if (WEXITSTATUS(status) == EXIT_FAILURE) {
        perror("");
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