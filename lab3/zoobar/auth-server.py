#!/usr/bin/python3

import rpclib
import sys
import auth
from debug import *

class AuthRpcServer(rpclib.RpcServer):
    def rpc_login(self,username,password):
        return auth.login(username,password)

    def rpc_register(self,username,password):
        print("registering user %s" % username) 
        print("password %s" % password)
        return auth.register(username,password)
        
    def rpc_check_token(self,username,token):
        return auth.check_token(username,token)


(dummy_zookld_fd, sockpath) = sys.argv
s = AuthRpcServer()
s.run_sockpath_fork(sockpath)