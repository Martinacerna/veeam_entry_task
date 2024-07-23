
# Folder Synchronization Script

This Python script synchronizes files from a source folder to a replica folder at a specified interval. 
It ensures that the replica folder mirrors the content of the source folder by copying new files, replacing modified files, and deleting removed files. 
Logging is set up to capture all file operations to both a log file and the console.

## Prerequisites

- Python 3.12
- Required Python packages: `click`, `schedule`
- Environment is set using Poetry.

You can install the required packages by using poetry:

```sh
poetry install
```
## Usage
To run the script, use the following command:
```sh
python3 logic_for_synch.py <sync_interval> <log_file_path> <source_folder_path> <replica_folder_path>
```

- sync_interval: Interval in seconds, at which the synchronization should run.
- log_file_path: Path to the log file, where operations will be logged.
- source_folder_path: Path to the source folder to be synchronized.
- replica_folder_path: Path to the replica folder, where files will be mirrored.

```sh
python3 logic_for_synch.py 60 /path/to/log_file.log /path/to/source_folder /path/to/replica_folder
```

### Contributors
Martina Divinová
