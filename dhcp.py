#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys, os, re, getopt, getpass, pexpect

def startup():
    user_id = raw_input('Brukernavn: ')
    password = getpass.getpass('Passord: ')
    subnet = raw_input('Hvilket subnet vil du jobbe med? ')
    return user_id, password, subnet

def loginSession(user_id, password):

    bofh = pexpect.spawn('bofh -u ' + user_id)
    if bofh.expect('Password for ' + user_id) == 0:
        bofh.sendline(password)
    else:
        exit(1)

    return bofh

def test(bofh):

    bofh.sendline('user info oysteirs')
    bofh.expect('Spreads:')
    print bofh.before
    print bofh.after

def gatherSubnetData(bofh, subnet):

    bofh.sendline('host used_list ' + subnet)
    if bofh.expect('In total:') == 0:
        subnetlist = bofh.before
        subnetNameList = subnetlist.split('\r\n')
        mod = []
        p = re.compile(r'hf-\d+-\d+\.uio.no')
        for line in subnetNameList:
            mod.append(p.findall(line))
        mod2 = filter(None, mod)
        mod = sum(mod2, [])

        f = open('subnetnames.txt', 'w')
        for item in mod:
            print>>f, item
        f.close()
        return mod
        #print mod
    else:
        print 'Feil med subnetliste eller tilgang.\nLogg inn på nytt'
        bofh.close()
        exit(1)

def checkFreeIP(bofh, subnetList):

    listOfFreeIP = []

    for ip in subnetList:
        bofh.sendline('host info ' + ip)
        if bofh.expect(['MAC.*<not set>', '[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}', pexpect.EOF, pexpect.TIMEOUT], timeout=3) == 1:
            listOfFreeIP.append(ip)
    return listOfFreeIP

#def findFirstFreeIP(bofh, subnetList):
#
#    for ip in subnetList:
#        check = bofh.sendline('host info ' + ip)
#        if bofh.expect(['[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}', pexpect.EOF, pexpect.TIMEOUT], timeout=3) == 0:
#            print ip
#        else:
#        #if check > 20 and bofh.expect(['<not set>', pexpect.EOF, pexpect.TIMEOUT]) == 0:
#            return ip

def findFirstFreeIP(bofh, subnetList):

    for ip in subnetList:
        bofh.sendline('host info ' + ip)
        if bofh.expect(['MAC.*<not set>', '[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}', pexpect.EOF, pexpect.TIMEOUT], timeout=3) == 0:
            return ip

def findMAC(bofh, subnetList, mac):

    for ip in subnetList:
        bofh.sendline('host info ' + ip)
        if bofh.expect(['MAC.*<not set>', '[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}', pexpect.EOF, pexpect.TIMEOUT], timeout=3) == 1:
            if bofh.after == mac:
                return ip
                #print mac + ' har maskinnavn: ' + ip
                #break
            #else:
                #print 'ikke ' + ip

#def pingDead(bofh, subnetList):

 #   for ip in subnetList:
        

def runMenu(bofh, subnet):

    subnetCheck = False
    subnetList = []
    freeCheck = False
    freeIP = []

    ans = True
    while ans:

        print"""
        bofh - dhcp

        1. Reservere spesifikk IP
        2. Reservere tilfeldig IP - tfinne første IP
        3. Fjerne IP-assosiasjon - kjøre sjekk
        4. Kontrollere IP
        5. Søke etter MAC-adresse
        6. Sjekke hvor mange ledige adresser
        7. Liste ledige adresser
        8. Sjekke etter døde adresser
        9. Rydde nettverk
        0. Avslutte
        """
        ans = input("Valg: ")
        if ans == 1:
            print("\nReservere spesifikk IP")
            reserveIP(bofh)
        elif ans == 2:
            print("Reservere tilfeldig IP")
            if not subnetCheck:
                subnetList = gatherSubnetData(bofh, subnet)
                subnetCheck = True
            print 'First free ip: ' + findFirstFreeIP(bofh, subnetList)
        elif ans == 3:
            print("Fjerne IP-assosiasjon")
            subnetList = gatherSubnetData(bofh, subnet)
            subnetCheck = True
        elif ans == 4:
            print("test")
            test(bofh)
        elif ans == 5:
            print 'MAC-adresse det skal søkes på (format 12:34:56:78:90:ab)'
            mac = raw_input('MAC: ')
            print mac + ' har maskinnavn ' + findMAC(bofh, subnetList, mac)
        elif ans == 6:
            if not subnetCheck:
                subnetList = gatherSubnetData(bofh, subnet)
                subnetCheck = True
            if not freeCheck:
                freeIP = checkFreeIP(bofh, subnetList)
                freeCheck = True
            print 'Ledige adresser på subnet %s: %s' % (subnet, len(freeIP))
        elif ans == 7:
            if not subnetCheck:
                subnetList = gatherSubnetData(bofh, subnet)
                subnetCheck = True
            if not freeCheck:
                freeIP = checkFreeIP(bofh, subnetList)
                freeCheck = True
            for item in freeIP:
                print item
            save = raw_input('\nSkal listen lagres til txt? (y/n): ')
            if save == 'y':
                f = open(subnet + '-free.txt', 'w')
                for item in freeIP:
                    print>>f, item
                f.close()
        elif ans == 8:
            pingDead

        elif ans == 0:
            ans = False

def reserveIP(bofh):

    ip = raw_input('IP-adresse: ')
    mac = raw_input('MAC-adresse: ')
    #bofh.sendline('dhcp assoc ' + ip + ' ' + mac)
    print 'Jada masa'


def printStuff(user_id):
    print 'U:', user_id

if __name__ == "__main__":
    #options, args = getopt.getopt(sys.argv[1:])

    user_id, password, subnet = startup()
    subnet = '129.240.'+subnet

    bofh = loginSession(user_id, password)

    os.system('clear')
    runMenu(bofh, subnet)


    
    bofh.close()
