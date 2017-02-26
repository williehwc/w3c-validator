#!/usr/bin/env python
'''
w3c-validator - Validate HTML and CSS files using the WC3 validators

Copyright: Stuart Rackham (c) 2011
License:   MIT
Email:     srackham@gmail.com
'''

import os
import sys
import time
import json
import commands
import urllib

css_validator_url = 'http://jigsaw.w3.org/css-validator/validator'
html_validator_url = 'https://validator.w3.org/nu/?out=text&level=error'

verbose_option = False

def message(msg):
    print >> sys.stderr, msg

def verbose(msg):
    if verbose_option:
        message(msg)

def validate(filename):
    '''
    Validate file and return JSON result as dictionary.
    'filename' can be a file name or an HTTP URL.
    Return '' if the validator does not return valid JSON.
    Raise OSError if curl command returns an error status.
    '''
    quoted_filename = urllib.quote(filename)
    if filename.startswith('http://'):
        # Submit URI with GET.
        if filename.endswith('.css'):
            cmd = ('curl -sG -d uri=%s -d warning=0 %s'
                    % (quoted_filename, css_validator_url))
        else:
            cmd = ('curl -sG -d uri=%s %s'
                    % (quoted_filename, html_validator_url))
    else:
        # Upload file as multipart/form-data with POST.
        if filename.endswith('.css'):
            cmd = ('curl -sF "file=@%s;type=text/css" -F output=json -F warning=no %s'
                    % (filename, css_validator_url))
        else:
            cmd = ('curl -s -H "Content-Type: text/html; charset=utf-8" --data-binary @%s "%s"'
                    % (filename, html_validator_url))
    verbose(cmd)
    status,output = commands.getstatusoutput(cmd)
    if status != 0:
        raise OSError (status, 'failed: %s' % cmd)
    verbose(output)
    return output


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--verbose':
        verbose_option = True
        args = sys.argv[2:]
    else:
        args = sys.argv[1:]
    errors = 0
    warnings = 0
    if len(sys.argv) >= 2 and sys.argv[1] == '--css':
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(os.getcwd()) for f in filenames if os.path.splitext(f)[1] == '.css']
        pass_phrase = '"errorcount"   : 0,'
    else:
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(os.getcwd()) for f in filenames if os.path.splitext(f)[1] == '.htm' or os.path.splitext(f)[1] == '.html']
        pass_phrase = 'The document validates according to the specified schema(s).'
    for f in files:
        message('validating: %s ...' % f)
        retrys = 0
        while retrys < 2:
            result = validate(f)
            if result:
                break
            retrys += 1
            message('retrying: %s ...' % f)
        else:
            message('failed: %s' % f)
            errors += 1
            continue
        if pass_phrase not in result:
            print('=== ' + os.path.basename(os.path.normpath(f)) + ' ===')
            print(result + '\n')
    if errors:
        exit(1)
