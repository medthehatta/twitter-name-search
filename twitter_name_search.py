#!/usr/bin/env python3
# coding: utf8

import requests
import time
import sys
import argparse

from itertools import product


alphabet = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ_'
file_prefix = 'twitnames'


def progress_filename(n):
    return '/var/tmp/{0}_{1}'.format(file_prefix, n)


def make_username_generator(length=None):
    return enumerate(''.join(x) for x in product (*[alphabet]*length))


def resume_index(savefile):
    """Get the resume_index from the `savefile`, or return 0 if no savefile"""
    try:
        with open(savefile) as f:
            return int(f.read().strip())
    except FileNotFoundError:
            return 0


def get_user_code(user):
    """Retrieve the response code for a user from Twitter"""
    user_page = 'https://twitter.com/{0}'.format(user)
    return requests.get(user_page).status_code


def report_code_for_user(code, user):
    """Given an HTTP return code from the user page, determines what class the
    user is in."""
    code_map = {
        404: 'free',
        200: 'unavailable',
        302: 'suspended',
    }

    status = code_map.get(code)

    if status:
        print('{0} {1}'.format(status, user))
    else:
        print('Error getting user "{0}": HTTP response {1}'.format(user, code))


def wait_for_webserver():
    print('Sleeping for 5 seconds...', file=sys.stderr)
    time.sleep(5)


def save_progress(path, last):
    with open(path,'w') as f:
        f.write(str(last))


def divides(i, freq):
    """Does `i` divide `freq`?  No if `i==0`."""
    return (i % freq == 0 and i != 0)


def resume(gen, start=0):
    """Skip to the `start`th element of the generator `gen`"""
    for _ in range(start): next(gen)


def main(length=3, sleep_freq=8, save_freq=10, reset=False):

    # Get the generator that produces all possible usernames with the given
    # length
    user_generator = make_username_generator(
        length=length,
    )

    progress_file = progress_filename(length)

    # What generator index should we resume from?
    last = 0 if reset else resume_index(progress_file)
    resume(user_generator, start=last)

    for i, user in user_generator:

        if divides(i, sleep_freq): wait_for_webserver()
        if divides(i, save_freq): save_progress(progress_file, i)

        report_code_for_user(
            get_user_code(user),
            user,
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--length', type=int, help='length of username')
    parser.add_argument(
        '--sleep-frequency',
        default=5,
        type=int,
        help='how frequently to wait for the webserver',
    )
    parser.add_argument(
        '--save-frequency',
        default=10,
        type=int,
        help='how frequently to save the progress',
    )
    parser.add_argument(
        '-r',
        '--reset',
        action='store_true',
        default=False,
        help='whether to start over or resume',
    )

    parsed = parser.parse_args()

    main(
        length=parsed.length,
        sleep_freq=parsed.sleep_frequency,
        save_freq=parsed.save_frequency,
        reset=parsed.reset,
    )

