#!/usr/bin/env python3

import logging
import os.path
import tempfile

import restic

logger = logging.getLogger(__name__)


def configure_logging():

    class ShutdownHandler(logging.StreamHandler):

        def emit(self, record):
            super().emit(record)
            if record.levelno >= logging.CRITICAL:
                raise SystemExit(255)

    root_logger = logging.getLogger()
    handler = ShutdownHandler()
    formatter = logging.Formatter('%(name)-15s %(levelname)-4s %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)


configure_logging()

version_info = restic.version()
logger.info('Running end-to-end tests with restic version %s (%s/%s/go%s)',
            version_info['restic_version'], version_info['architecture'],
            version_info['platform_version'], version_info['go_version'])

PASSWORD = 'mysecretpass'
PASSWORD_FILE = tempfile.NamedTemporaryFile()
PASSWORD_FILE.write(PASSWORD.encode('utf-8'))
PASSWORD_FILE.flush()

DUMMY_SOURCE_DIR = tempfile.mkdtemp()
DUMMY_DATA_PATH = os.path.join(DUMMY_SOURCE_DIR, 'mydata.txt')
with open(DUMMY_DATA_PATH, 'w') as dummy_data_file:
    dummy_data_file.write('some data to back up')

restic.binary_path = 'restic'
restic.repository = tempfile.mkdtemp()
restic.password_file = PASSWORD_FILE.name

logger.info('Initializing repository')
restic.init()

logger.info('Backing up %s', DUMMY_DATA_PATH)
restic.backup(paths=[DUMMY_DATA_PATH])

RESTORE_DIR = tempfile.mkdtemp()
logger.info('Restoring to %s', RESTORE_DIR)
restic.restore(snapshot_id='latest', target_dir=RESTORE_DIR)

RESTORED_DATA_PATH = os.path.join(RESTORE_DIR, DUMMY_DATA_PATH)
if not os.path.exists(RESTORED_DATA_PATH):
    logger.fatal('Expected to find %s', RESTORED_DATA_PATH)
RESTORED_DATA = open(RESTORED_DATA_PATH).read()
if RESTORED_DATA != 'some data to back up':
    logger.fatal('Expected to restored file to contain %s (got %s)',
                 'some data to back up', RESTORED_DATA)

logger.info('End-to-end test succeeded!')
