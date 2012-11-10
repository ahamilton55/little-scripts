#!/usr/bin/env python2

"""
Create a group of basic Nagios hosts from a Cobbler system
"""
import xmlrpclib
from optparse import OptionParser
from ConfigParser import SafeConfigParser
import re
import os
import subprocess

def create_system_in_nagios(template, system_info, my_config):
                        #cattle_dir, prod_dir, interface, domain):
    """
    From a template create the Nagios host entry file from the information
    found in Cobbler in system_info
    """
    if not os.path.exists(template):
        print "Error: Nagios template {0} was not found.".format(template)
        exit (1)

    if not os.path.exists(my_config['prod_dir'] + "/" +
                          system_info['hostname'] + ".cfg"):

        filename = '{0}{1}.cfg'.format(my_config['cattle_dir'], 
                                       system_info['hostname'])

        template_file = open(template)
        new_file = open(filename, 'w')

        for line in template_file.readlines():
            if "%hostname%" in line:
                hostname = system_info['hostname']

                match = re.compile('%hostname%')
                line = re.sub(match, hostname, line)

            elif "%alias%" in line:
                hostname = system_info['hostname']

                alias_match = re.compile(my_config['domain'])
                alias = re.sub(alias_match, '', hostname)

                match = re.compile('%alias%')
                line = re.sub(match, alias, line)

            elif "%ip_address%" in line:
                ip_addr = system_info['interfaces'][my_config['interface']]['ip_address']

                match = re.compile('%ip_address%')
                line = re.sub(match, ip_addr, line)

            new_file.write(line)

        template_file.close()
        new_file.close()

def create_hostgroup_file(template, cattle, cattle_dir):
    """
    From a template file create a host group entry for the cattle servers found
    on the Cobbler server.
    """
    name = "cattle"
    alias = "The Eucalyptus Cattle"

    if not os.path.exists(template):
        print "Error: Template template_file {0} does not exists!".format(template)
        exit(1)

    hostgroup_file = "{0}/cattle_hostgroup.cfg".format(cattle_dir)

    template_file = open(template)
    hostgroup_file = open(hostgroup_file, 'w')

    for line in template_file.readlines():
        if "%systems%" in line:
            match = "%systems%"
            line = re.sub(match, cattle, line)
        elif "%name%" in line:
            match = "%name%"
            line = re.sub(match, name, line)
        elif "%alias%" in line:
            match = "%alias%"
            line = re.sub(match, alias, line)

        hostgroup_file.write(line)

    template_file.close()
    hostgroup_file.close()

def main():
    """
    Main function for building out the Nagios files for the cattle (non-production)
    systems in Cobbler.
    """
    default_conf = 'config.conf'
    cattle = ""
    systems = []

    parser = OptionParser()
    parser.add_option("-c", "--config", action="store", dest="config",
                type="string", help="configuration file to be used.")

    (options, args) = parser.parse_args()

    config = SafeConfigParser()

    if not options.config == "":
        config.read(options.config)
    else:
        config.read(default_conf)

    server_url = "http://{0}/cobbler_api".format(config.get('Cobbler','server'))
    remote = xmlrpclib.Server(server_url)
    systems = remote.find_system({'name': '*'})

    for system in systems:
        system_info = remote.get_system(system)
        create_system_in_nagios(config.get('Nagios', 'template'), system_info, {
                                'cattle_dir': config.get('Nagios', 'cattle_dir'),
                                'prod_dir': config.get('Nagios', 'prod_dir'),
                                'interface': config.get('Cobbler', 'interface'),
                                'domain': config.get('Cobbler', 'domain')})

        if not os.path.exists(config.get('Nagios', 'prod_dir') + "/" + 
                                        system_info['hostname'] + ".cfg"):
            if cattle == "":
                cattle += system_info['hostname']
            else:
                cattle += "," + system_info['hostname']

    create_hostgroup_file(config.get('Nagios', 'hostgroup_template'), 
                            cattle, config.get('Nagios', 'cattle_dir'))
    nagios_cmd = "nagios -v {0}".format(config.get('Nagios', 'conf'))
    nagios_rtn = subprocess.call(nagios_cmd)

    if not nagios_rtn == 0:
        print "Error: Nagios configuration is broken somewhere. Please check \
        it manually with {0}".format(nagios_cmd)
        exit(2)
    else:
        nagios_rtn = subprocess.call('service nagios reload')
        if not nagios_rtn == 0:
            print "Error: Nagios did not properly reload!"
            exit(3)

if __name__ == '__main__':
    main()
    exit(0)
