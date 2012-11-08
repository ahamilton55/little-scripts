#!/usr/bin/env python2
import clbr_config

def connect_to_cobbler(server, username, password):
    """
    Make the connection to the cobbler server that will be used for the
    all operations on the system. This will keep from having to make a 
    connection everytime we perform an operation on the server and should
    keep a (possible) huge connection load on the cobbler server

    server -- The IP or FQDN of the cobbler server
    username -- Username with admin rights on the cobbler server
    password -- Password of the corresponding username above
    """

    remote = xmlrpclib.Server("http://" + server + "/cobbler_api")
    token = remote.login(username, password)

    return remote, token

def main():
    remote, token = connect_to_cobbler(cblr_config.CBLR_SERVER, cblr_config.CBLR_USER, 
                                       cblr_config.CBLR_PASS)

    parser = OptionParser()
    parser.add_option("--set-password", action="store_true", dest="set_password", default=False,
        help="set the password of the pod to 'eucalyptus' and can only be used entire pods")
    parser.add_option("--all-pods", action="store_true", dest="all_pods", default=False,
        help="apply the operation to all pods")
    parser.add_option("--pod", action="append", type="string", dest="pods",
        help="used to select pods")
    parser.add_option("--frontend", action="append", type="string", dest="frontends",
        help="used to select frontends")
    parser.add_option("--node", action="append", type="string", dest="nodes",
        help="used to select nodes")
    parser.add_option("--get-profiles", action="store_true", dest="get_profiles", default=False,
        help="provide a list of available profiles")
    parser.add_option("--set-profile", action="store", type="string", dest="profile",
        help="set the lists systems with the profile provided")
    parser.add_option("--start-range", action="store", type="int", dest="start_range",
        help="starts a range of pods to use")
    parser.add_option("--end-range", action="store", type="int", dest="end_range",
        help="ends a range of pods to use")
    parser.add_option("--debug", action="store_true", dest="debug", default=False,
        help="show what the program has received from the command line")

    (options, args) = parser.parse_args()

if __name__ == '__main__':
    main()
    exit(0)
