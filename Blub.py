#!/usr/bin/env python2
# coding=UTF-8

if __name__ == '__main__':
    timeout = 2
    url = "aaa"
    cmdstr = "timeout -k {longerTimeout}s {longerTimeout}s siege -c 100 -t {timeout} {url}"\
        .format(longerTimeout=timeout + 2, timeout=timeout, url=url)
    print cmdstr