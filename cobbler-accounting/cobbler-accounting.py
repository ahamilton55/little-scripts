#!/usr/bin/env python2
"""
Figures out how many machines each user is using as well as how many systems
remain in each group's pool.
"""

import xmlrpclib
import operator
from ConfigParser import SafeConfigParser
from optparse import OptionParser

def main():
    groups = ""
    cblr_url = ""
    users = {}

    parser = OptionParser()
    parser.add_option("-c", "--config", action="store", dest="config",
                type="string", help="configuration file to be used.")
    parser.add_option("-u", "--users-file", action="store", dest="user_file",
                type="string", help="Cobbler users.conf file to use")
    parser.add_option("-s", "--server", action="store", dest="server",
                type="string", help="Cobbler server hostname or IP")

    (options, args) = parser.parse_args()

    if options.server:
        cblr_url = "http://{0}/cobbler_api".format(options.server)
    else:
        cblr_url = "http://cobbler.eucalyptus-systems.com/cobbler_api"

    if options.user_file:
        config = SafeConfigParser()
        config.read(options.user_file)
        groups = config.sections()

    remote = xmlrpclib.Server(cblr_url)

    systems = remote.find_system({'name': '*'})

    for system in systems:
        system_info = remote.get_system(system)
        owners = system_info['owners']
        for owner in owners:
            if owner in users:
                users[owner] += 1
            else:
                users[owner] = 1

    sorted_users = sorted(users.iteritems(), key=operator.itemgetter(1),
                            reverse=True)

    #Print out the users and taken systems
    user_title = "User\t\t# of systems taken"
    print user_title
    print "-"*len(user_title.expandtabs())

    for user in sorted_users:
        if not user[0] in groups:
            if len(user[0]) >= 8:
                print "{0}\t{1}".format(user[0], user[1])
            else:
                print "{0}\t\t{1}".format(user[0], user[1])

    print

    # Print out the groups and remaining systems
    group_title = "Group\t\t# of Systems remaining"
    print group_title
    print "-"*len(group_title.expandtabs())

    for user in sorted_users:
        if user[0] in groups:
            if len(user[0]) >= 8:
                print "{0}\t{1}".format(user[0], user[1])
            else:
                print "{0}\t\t{1}".format(user[0], user[1])

    print

if __name__ == "__main__":
    main()
