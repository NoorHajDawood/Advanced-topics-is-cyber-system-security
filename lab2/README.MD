**NOTES**

1- exploit-template.py : Bader: we need to change it to make the attack maybe change from get to post
2- shellcode.S : שתילת קוד,צריך לשינוי כך שקובץ סי יריץ אותו ויגרום לשרת לעשות אותו
3- we can steel from another users by transfer negative numbers like -2
4- we can add to my self more animals by transfer to my self a positive number like 5
5- we can get in Internal Server Error status code 500 by transfer string instead of number
6- Cannot transfer 0
7- Cannot enter big input on user name and password it will crash
8- Stucl in infintie loop : send http request that doesn't end in with \r\n\r\n" end with \r\n


## LAB 1 ##
** kill process: kill $(lsof -t -i:8080)**

1) gdb zookd
2) set follow-fork-mode child
3) b http_request_headers
4) b main
5) r 8080
6) Breakpoint 1, main (argc=2, argv=0x7fffffffe318) at zookd.c:25
25          if (argc != 2)
7) c -> Continuing.
8) python3 exploit-template.py localhost 8080
9) Thread 2.1 "zookd" hit Breakpoint 1, http_request_headers (fd=4) at http.c:127
10) in exploit-template.py we've set an http header wilth value big enough to overflow the "value[512]" and overflows the stack in http_request_headers.
after sending the http request, we'll stop in the breakpoint of http_request_headers.
there we'll see that the function url_decode doesn't check for the length of the value copied to "value" which causes the buffer overflow
when attempting to return from the function http_request_headers, the return address is replaced with an invalid address which crashes the process


## LAB 2 ##

step 1:
    we change the line 21 in shellcode.S to $SYS_unlink to delete the file
    To test the stackover flow we need to test this func $1 = {void ()} 0x555555556f8e <stacktest>
    $1 = {void ()} 0x555555556f93 <stacktest>


solution step 2:

*** original return address : 0x555555556ba7
    x/150x &value :
    **d170 - cf40 = 560**
    0x7fffffffd170 (this line that **(return address)** exist at the secound part the last two 4 bytes=> **0x7fffffffd170+8=> return address** ) -  0x7fffffffcf40 (this start address of the **value variable**) = 
    return address => 560+8




VURNABILITES LIST => OWASP TOP 10