#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>

#define INPUT_SIZE 1024


pid_t childPid = 0;

void executeShell(int timeout);

void writeToStdout(char *text);

void alarmHandler(int sig);

void sigintHandler(int sig);

char *trim(char *str);

char *getCommandFromInput();

void registerSignalHandlers();

void killChildProcess();

int main(int argc, char **argv) {
    registerSignalHandlers();

    int timeout = 0;
    if (argc == 2) {
        timeout = atoi(argv[1]);
    }

    if (timeout < 0) {
        writeToStdout("Invalid input detected. Ignoring timeout value.\n");
        timeout = 0;
    }

    while (1) {
        executeShell(timeout);
    }

    return 0;
}

/* Sends SIGKILL signal to a child process.
 * Error checks for kill system call failure and exits program if
 * there is an error */
void killChildProcess() {
    if (kill(childPid, SIGKILL) == -1) {
        perror("Error in kill");
        exit(EXIT_FAILURE);
	}
}

/* Signal handler for SIGALRM. Catches SIGALRM signal and
 * kills the child process if it exists and is still executing.
 * It then prints out penn-shredder's catchphrase to standard output */
void alarmHandler(int sig) {
    char *catchphrase = "Bwahaha ... tonight I dine on turtle soup\n";
    killChildProcess();
    writeToStdout(catchphrase);
}

/* Signal handler for SIGINT. Catches SIGINT signal (e.g. Ctrl + C) and
 * kills the child process if it exists and is executing. Does not
 * do anything to the parent process and its execution */
void sigintHandler(int sig) {
	if (childPid != 0) {
    	killChildProcess();
    }
}

/* Registers SIGALRM and SIGINT handlers with corresponding functions.
 * Error checks for signal system call failure and exits program if
 * there is an error */
void registerSignalHandlers() {
    if (signal(SIGINT, sigintHandler) == SIG_ERR) {
        perror("Error in signal");
        exit(EXIT_FAILURE);
    }
    if (signal(SIGALRM, alarmHandler) == SIG_ERR) {
        perror("Error in signal");
        exit(EXIT_FAILURE);
    }
}

/* Prints the shell prompt and waits for input from user.
 * Takes timeout as an argument and starts an alarm of that timeout period
 * if there is a valid command. It then creates a child process which
 * executes the command with its arguments.
 *
 * The parent process waits for the child. On unsuccessful completion,
 * it exits the shell. */
void executeShell(int timeout) {
    char *command;
    char temp[INPUT_SIZE];
    char *input;
    int status;
    char minishell[] = "penn-shredder# ";
    writeToStdout(minishell);

    input = getCommandFromInput();
    if (input != NULL) {
        strcpy(temp, input);
        free(input);
        command = trim(temp);
    }
    else {
        free(input);
        char *exit_phrase = "Exiting...\n";
        writeToStdout(exit_phrase);
        exit(0);
    }
    if (strcmp(command, "") == 0) {
        //if command is empty, do nothing
        return;
    }

    if (command != NULL) {

        childPid = fork();

        if (childPid < 0) {
            perror("Error in creating child process");
            exit(EXIT_FAILURE);
        }

        if (childPid == 0) {
            // child
            char *const envVariables[] = {NULL};
            char *const args[] = {command, NULL};
            if (execve(command, args, envVariables) == -1) {
                perror("Error in execve");
                exit(EXIT_FAILURE);
            }
        } else {
            // parent
            alarm(timeout);
            do {
                if (wait(&status) == -1) {
                    perror("Error in child process termination");
                    exit(EXIT_FAILURE);
                }
            } while (!WIFEXITED(status) && !WIFSIGNALED(status));
            // reset childPid
            childPid = 0;
            // cancel alarm signal if applicable
            alarm(0);
        }
    }
}

/* Writes particular text to standard output */
void writeToStdout(char *text) {
    if (write(STDOUT_FILENO, text, strlen(text)) == -1) {
        perror("Error in write");
        exit(EXIT_FAILURE);
    }
}

char *trim(char *str) {
    if (str == NULL) {
        return NULL;
    }
    if (str[0] == '\0') {
        return str;
    }
    char *end = str + strlen(str);
    while (*str == 32 && str != end) { //32 is acsii for space
        str++;
    }
    if (str == end) {
        return "";
    }
    end--;
    while (*end == 32) {
        end--;
    }
    end++;
    *end = '\0';
    return str;
}

/* Reads input from standard input till it reaches a new line character.
 * Checks if EOF (Ctrl + D) is being read and exits penn-shredder if that is the case
 * Otherwise, it checks for a valid input and adds the characters to an input buffer.
 *
 * From this input buffer, the first 1023 characters (if more than 1023) or the whole
 * buffer are assigned to command and returned. An \0 is appended to the command so
 * that it is null terminated */
char *getCommandFromInput() {
    char *input = (char*) malloc(INPUT_SIZE);
    if (input == NULL) {
    	perror("Error in malloc");
        exit(EXIT_FAILURE);
    }
    *input = '\0';
    int length = 0;
    // read in one char at a time so we can catch an EOF and not append a '\n'
    while (1) {
    	char one;
    	int size = read(STDIN_FILENO, &one, 1);
    	if (size < 1 || one == EOF) {
    		free(input);
    		return NULL;
    	}
    	else if (one == '\n') {
    		return input;
    	}
    	else {
    		length++;
    		if (length < INPUT_SIZE - 1) {
    			strcat(input, (char[2]) {one, '\0'});
    		} else {
                return input;    			
    		}
    	}
    }
}