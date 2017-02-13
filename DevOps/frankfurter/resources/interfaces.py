#!/usr/bin/env python3

"""
interfaces -- Create and copy a custom network interface
"""

import os
import paramiko
from scp import SCPClient

HOST = '192.168.7.2'
USERNAME, PASSWORD = 'ubuntu', 'temppwd'
TMP_FILE_PATH = '/tmp/interfaces'


def read_team_number(prompt='Enter the team number: '):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print('Not a number.')


def build_custom_config(team_number):
    with open('interfaces') as network_config_file:
        for line in network_config_file:
            if line.startswith('iface ra0'):
                line = line.replace('dhcp', 'static')
            yield line[:-1]  # Take off the newline
            if 'wpa-psk' in line:
                indent = ' '*4
                yield indent + 'address 192.168.128.{0}'.format(team_number)
                yield indent + 'netmask 255.255.255.0'
                yield indent + 'network 192.168.128.0'
                yield indent + 'gateway 192.168.128.1'


def write_tmp_file(lines):
    with open(TMP_FILE_PATH, 'w+') as tmp_file:
        print('\n'.join(lines), file=tmp_file)


def copy_network_config_file():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USERNAME, password=PASSWORD)

    scp = SCPClient(ssh.get_transport())
    scp.put(TMP_FILE_PATH, '/etc/network')

    ssh.close()


def delete_tmp_file():
    os.remove(TMP_FILE_PATH)


def main():
    team_number = read_team_number()
    lines = build_custom_config(team_number)
    write_tmp_file(lines)
    # copy_network_config_file()
    # delete_tmp_file()


if __name__ == '__main__':
    main()
