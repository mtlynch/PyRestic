# resticpy API

## Global options

| Option                   | Default Value | Notes |
|--------------------------|---------------|-------|
| `restic.binary_path`     | `'restic'`    | Specifies the location of your restic binary if it's not in the user's default path. (e.g., `/path/to/restic.exe`) |
| `restic.repository`      | `None`      | Specifies the path or URL of your restic backup repository. |
| `restic.password_file`   | `None`      | Specifies the path to the file containing your restic repository password. |

## `backup`

### Args

* `paths`: A list of paths to files or directories to back up
* `exclude_patterns`: A list of patterns of path exclusions
* `exclude_files`: A list of files containing exclude lists

### Returns

A dictionary with a summary of the backup result.

### Example

```python
>>> restic.backup(paths=['/data/music'],
                  exclude_patterns=['Justin Bieber*', 'Selena Gomez*'],
                  exclude_files=['bad-songs.txt'])
{
  "message_type": "summary",
  "files_new": 1,
  "files_changed": 0,
  "files_unmodified": 0,
  "dirs_new": 2,
  "dirs_changed": 0,
  "dirs_unmodified": 0,
  "data_blobs": 1,
  "tree_blobs": 3,
  "data_added": 1133,
  "total_files_processed": 1,
  "total_bytes_processed": 20,
  "total_duration": 0.211291367,
  "snapshot_id": "e17049ab"
}
```

## `forget`

### Args

* `prune`: A boolean representing whether to automatically run the 'prune' command if snapshots have been removed
* `keep_daily`: An int representing the last N daily snapshots to keep

### Returns

A dictionary with a summary of the forget result.

### Example

```python
>>> restic.forget(prune=True, keep_daily=4)
[{
  'tags': None,
  'host': 'ecb5551395ae',
  'paths': ['/tmp/tmp6ew1vzp2/mydata.txt'],
  'keep': [{
      'time': '2021-03-16T00:10:37.015657013Z',
      'tree': '4483c2c6c1386abb9f47497cf108bab19e09c42430d32cd640a4f6f97137841f',
      'paths': ['/tmp/tmp6ew1vzp2/mydata.txt'],
      'hostname': 'ecb5551395ae',
      'username': 'demouser',
      'uid': 3434,
      'gid': 3434,
      'id': '3f6de49c6461ffd42900a204655708a3e136a3814abe298c07f27e412e2b6a43',
      'short_id': '3f6de49c'
  }],
  'remove': None,
  'reasons': [{
      'snapshot': {
          'time': '2021-03-16T00:10:37.015657013Z',
          'tree': '4483c2c6c1386abb9f47497cf108bab19e09c42430d32cd640a4f6f97137841f',
          'paths': ['/tmp/tmp6ew1vzp2/mydata.txt'],
          'hostname': 'ecb5551395ae',
          'username': 'demouser',
          'uid': 3434,
          'gid': 3434
      },
      'matches': ['daily snapshot'],
      'counters': {
          'daily': 4
      }
  }]
}]
```

## `generate`

TODO(mtlynch): Write this.

## `init`

TODO(mtlynch): Write this.

## restore

TODO(mtlynch): Write this.

## `self_update`

TODO(mtlynch): Write this.

## `stats`

TODO(mtlynch): Write this.

## `version`

TODO(mtlynch): Write this.
