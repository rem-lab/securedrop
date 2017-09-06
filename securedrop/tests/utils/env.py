# -*- coding: utf-8 -*-
"""Testing utilities related to setup and teardown of test environment.
"""
import os
from os.path import abspath, dirname, exists, isdir, join, realpath
import journalist
import shutil
import subprocess
import threading

import gnupg

os.environ['SECUREDROP_ENV'] = 'test'  # noqa
import config
import crypto_util
from db import init_db, db_session

FILES_DIR = abspath(join(dirname(realpath(__file__)), '..', 'files'))


def create_directories():
    """Create directories for the file store and the GPG keyring.
    """
    for d in (config.SECUREDROP_DATA_ROOT, config.STORE_DIR,
              config.GPG_KEY_DIR, config.TEMP_DIR):
        if not isdir(d):
            os.mkdir(d)


def init_gpg():
    """Initialize the GPG keyring and import the journalist key for
    testing.
    """
    gpg = gnupg.GPG(homedir=config.GPG_KEY_DIR)
    # Faster to import a pre-generated key than to gen a new one every time.
    for keyfile in (join(FILES_DIR, "test_journalist_key.pub"),
                    join(FILES_DIR, "test_journalist_key.sec")):
        gpg.import_keys(open(keyfile).read())
    return gpg


def setup():
    """Set up the file system, GPG, and database."""
    create_directories()
    init_gpg()
    init_db()
    # Do tests that should always run on app startup
    crypto_util.do_runtime_tests()
    journalist.shredder.start()


def teardown():
    # make sure threads launched by tests complete before
    # teardown, otherwise they may fail because resources
    # they need disappear
    journalist.shredder.stop()
    for t in threading.enumerate():
        if t.is_alive() and not isinstance(t, threading._MainThread):
            t.join()
    db_session.remove()
    try:
        shutil.rmtree(config.SECUREDROP_DATA_ROOT)
    except OSError as exc:
        os.system("find " + config.SECUREDROP_DATA_ROOT)  # REMOVE ME, see #844
        if 'No such file or directory' not in exc:
            raise
    except:
        os.system("find " + config.SECUREDROP_DATA_ROOT)  # REMOVE ME, see #844
        raise
