/* dispatch daemon */

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

static void process_client(int);
static int run_server(const char* port);

static int start_server(const char *portstr);
int sock_fd;
int main(int argc, char **argv)
{
    if (argc != 3)
        errx(1, "Wrong arguments");

    sock_fd = atoi(argv[1]);
    run_server(argv[2]);
}

/* socket-bind-listen idiom */
static int start_server(const char *portstr)
{
    struct addrinfo hints = {0}, *res;
    int sockfd;
    int e, opt = 1;

    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    if ((e = getaddrinfo(NULL, portstr, &hints, &res)))
        errx(1, "getaddrinfo: %s", gai_strerror(e));
    if ((sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol)) < 0)
        err(1, "socket");
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)))
        err(1, "setsockopt");
    if (fcntl(sockfd, F_SETFD, FD_CLOEXEC) < 0)
        err(1, "fcntl");
    if (bind(sockfd, res->ai_addr, res->ai_addrlen))
        err(1, "bind");
    if (listen(sockfd, 5))
        err(1, "listen");
    freeaddrinfo(res);

    return sockfd;
}

static int run_server(const char* port)
{
    int sockfd = start_server(port); 
    warnx("Listening on port %s", port);

    for (;;)
    {
        int cltfd = accept(sockfd, NULL, NULL);
        if (cltfd < 0)
            err(1, "accept");
        process_client(cltfd);
        close(cltfd);
    }
}

static void process_client(int fd)
{
    static char env[8192];
    static size_t env_len = 8192;
    char reqpath[4096];
    const char *errmsg;
    
        /* get the request line */
    if ((errmsg = http_request_line(fd, reqpath, env, &env_len)))
        return http_err(fd, 500, "http_request_line: %s", errmsg);

    if (sendfd(sock_fd, env, env_len, fd) < 0) 
        err(1, "ERROR sendfd socket:%d, fd:%d", sock_fd, fd);
}

void accidentally(void)
{
    __asm__("mov 16(%%rbp), %%rdi"
            :
            :
            : "rdi");
}
