#!/usr/bin/env python3

import json
import logging
import os.path
import tempfile

import restic

logger = logging.getLogger(__name__)

# pylint: disable=consider-using-with


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
with open(DUMMY_DATA_PATH, 'w', encoding='utf-8') as dummy_data_file:
    dummy_data_file.write('some data to back up')

primary_repo = tempfile.mkdtemp()

restic.binary_path = 'restic'
restic.repository = primary_repo
restic.password_file = PASSWORD_FILE.name

logger.info('Initializing repository')
logger.info(restic.init())

logger.info('Backing up %s', DUMMY_DATA_PATH)
backup_result = restic.backup(paths=[DUMMY_DATA_PATH])
logger.info('backup_result: %s', json.dumps(backup_result))
if backup_result['files_new'] != 1:
    logger.fatal('Expected 1 new file (got %d)', backup_result['files_new'])
if backup_result['files_changed'] != 0:
    logger.fatal('Expected 0 changed files (got %d)',
                 backup_result['files_changed'])

RESTORE_DIR = tempfile.mkdtemp()
logger.info('Restoring to %s', RESTORE_DIR)
logger.info(restic.restore(snapshot_id='latest', target_dir=RESTORE_DIR))

RESTORED_DATA_PATH = os.path.join(RESTORE_DIR, DUMMY_DATA_PATH)
if not os.path.exists(RESTORED_DATA_PATH):
    logger.fatal('Expected to find %s', RESTORED_DATA_PATH)
RESTORED_DATA_EXPECTED = 'some data to back up'
with open(RESTORED_DATA_PATH, encoding='utf-8') as f:
    RESTORED_DATA_ACTUAL = f.read()
if RESTORED_DATA_EXPECTED != RESTORED_DATA_ACTUAL:
    logger.fatal('Expected to restored file to contain %s (got %s)',
                 RESTORED_DATA_EXPECTED, RESTORED_DATA_ACTUAL)

snapshots = restic.snapshots(group_by='host')
logger.info('repo snapshots: %s', json.dumps(snapshots))

stats = restic.stats(mode='blobs-per-file')
logger.info('repo stats: %s', stats)
if stats['total_size'] != len(RESTORED_DATA_EXPECTED):
    logger.fatal('Expected to total size of %d (got %d)',
                 len(RESTORED_DATA_EXPECTED), stats['total_size'])

logger.info('pruning repo: %s', restic.forget(prune=True, keep_daily=5))

logger.info('check result: %s', restic.check(read_data=True))

# Initialiize a secondary repo
logger.info('making secondary repository')

PASSWORD2 = 'myothersecret'
PASSWORD_FILE2 = tempfile.NamedTemporaryFile()
PASSWORD_FILE2.write(PASSWORD2.encode('utf-8'))
PASSWORD_FILE2.flush()

secondary_repo = tempfile.mkdtemp()

restic.repository = secondary_repo
restic.password_file = PASSWORD_FILE2.name

logger.info(restic.init())

# Go back to original repo
restic.repository = primary_repo
restic.password_file = PASSWORD_FILE.name

logger.info(
    'repo copy result: %s',
    restic.copy(repo2=secondary_repo, password_file2=PASSWORD_FILE2.name))

logger.info('End-to-end test succeeded!')
