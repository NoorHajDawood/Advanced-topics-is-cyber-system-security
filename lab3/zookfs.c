#include "http.h"
#include <err.h>
#include <regex.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <netdb.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/param.h>
#include <sys/types.h>
#include <sys/socket.h>

void zooksvc(int, int);

int main(int argc, char **argv)
{
    int sock_fd;
    if (argc != 2)
        errx(1, "Wrong arguments");

    sock_fd = atoi(argv[1]);
    int fd = -1;

    for(;;) {
        zooksvc(fd, sock_fd);
    }
}

void zooksvc(int fd, int sock_fd)
{
    static char env[8192];
    static size_t env_len = 8192;
    const char *errmsg;

    if ((recvfd(sock_fd, env, env_len, &fd) <= 0) || fd < 0)
            err(1, "recvfd socket:%d, fd:%d", sock_fd, fd);
    // /* get the request line */
    // if ((errmsg = http_request_line(fd, reqpath, env, &env_len)))
    //     return http_err(fd, 500, "http_request_line: %s", errmsg);

    env_deserialize(env, sizeof(env));
    // printf("REQUEST_URI: %s\nPATH_INFO: %s\n", getenv("REQUEST_URI"), getenv("PATH_INFO"));
    /* get all headers */
    if ((errmsg = http_request_headers(fd)))
        http_err(fd, 500, "http_request_headers: %s", errmsg);
    else
        http_serve(fd, getenv("REQUEST_URI"));
    
    clearenv();
    close(fd);
}