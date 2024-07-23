import hashlib
import os
import shutil
import time

import click
import schedule

import logging

# Logger settings
# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def check_replica_exists(folder_path: str) -> None:
    """
    Function to check if replica folder exists, if not create one.
    :param folder_path: provided as CLI argument, str
    """
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        logger.info("Replica folder created.")
    return None


def create_folder_hash(folder_path: str) -> dict[str, str]:
    """
    Function to create a hash map from files in a folder. Uses hash_file_content function to create hash of each file.
    :param folder_path: path to the folder to hash, str
    :return: dict, hash map of files in folder. Structure is {hash of specific file: file_name}
    """
    hash_map = {}
    # Take only files and not folders
    folder_files = [
        item
        for item in os.listdir(folder_path)
        if not os.path.isdir(f"{folder_path}/{item}")
    ]
    for file in folder_files:
        hash_file = hash_file_content(folder_path, file)
        hash_map[hash_file] = file
    return hash_map


def hash_file_content(folder_path: str, file_name: str) -> str:
    """
    Function to hash the content of a file by using sha256 algorithm.
    :param folder_path: path to the folder where the file is located
    :param file_name: name of the file to hash
    :return: hash of the file content
    """
    with open(f"{folder_path}/{file_name}", "rb") as f:
        hashed_content = hashlib.file_digest(f, "sha256").hexdigest()
    return hashed_content


def copy_files(source_file_path: str, replica_file_path: str) -> None:
    """
    Function to copy file from one folder to another.
    :param source_file_path: path of the file to copy
    :param replica_file_path: path of folder where the file will be copied
    """
    shutil.copyfile(source_file_path, replica_file_path)
    logger.info(f"File {source_file_path} copied to {replica_file_path}")


def delete_files(file_path: str) -> None:
    """
    Function to delete a file.
    :param file_path: path of the file to delete
    """
    os.remove(file_path)
    logger.info(f"File {file_path} deleted.")


@click.command()
@click.argument("sync_interval", help="synchronization interval in seconds")
@click.argument(
    "log_file_path", help="where should be log file created if it does not exist, str"
)
@click.argument(
    "source_folder_path", help="path to the folder from which files will be copied, str"
)
@click.argument(
    "replica_folder_path",
    help="path to the folder where files from source folder will be copied, str",
)
def run(sync_interval, log_file_path, source_folder_path, replica_folder_path) -> None:
    """
    Setup logger and schedule the sync logic.
    :param sync_interval: provided as CLI argument, int
    :param log_file_path: provided as CLI argument, str
    :param source_folder_path: provided as CLI argument, str
    :param replica_folder_path: provided as CLI argument, str
    :return:
    """
    schedule.every(int(sync_interval)).seconds.do(
        logic, source_folder_path, replica_folder_path
    )

    # Create a formatter to define the log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Create a file handler to write logs1 to a file
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create a stream handler to print logs1 to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(
        logging.INFO
    )  # You can set the desired log level for console output
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    while True:
        schedule.run_pending()
        time.sleep(1)


def logic(source_folder_path: str, replica_folder_path: str) -> None:
    """
    Function to sync files in source folder to replica folder.
    :param source_folder_path: path of the folder to sync
    :param replica_folder_path: path of the folder where to sync files
    """

    check_replica_exists(replica_folder_path)
    _sync_files_in_folder(replica_folder_path, source_folder_path)

    source_folder_dirs = [
        item
        for item in os.listdir(source_folder_path)
        if os.path.isdir(f"{source_folder_path}/{item}")
    ]
    replica_folder_dirs = [
        item
        for item in os.listdir(replica_folder_path)
        if os.path.isdir(f"{replica_folder_path}/{item}")
    ]

    # if folder where files should be copied does not exist
    for missing_folder in set(source_folder_dirs) - set(replica_folder_dirs):
        os.mkdir(f"{replica_folder_path}/{missing_folder}")
        logger.info("Replica folder created")

    # delete folders that are in replica folder but not in source folder
    for folder_to_delete in set(replica_folder_dirs) - set(source_folder_dirs):
        shutil.rmtree(f"{replica_folder_path}/{folder_to_delete}")
        logger.info(f"Directory tree {replica_folder_path}/{folder_to_delete} deleted")

    # recursively run logic function for each folder and it's files
    for folder in source_folder_dirs:
        logic(f"{replica_folder_path}/{folder}", f"{source_folder_path}/{folder}")

    return None


def _sync_files_in_folder(replica_folder_path: str, source_folder_path: str) -> None:
    """
    Function to sync files in a folder.
    :param replica_folder_path: path of the folder where to sync files
    :param source_folder_path: path of the folder to sync
    """

    source_hash_map = create_folder_hash(source_folder_path)
    replica_hash_map = create_folder_hash(replica_folder_path)

    # delete files that are not in source folder
    source_file_set = set(source_hash_map.keys())
    replica_file_set = set(replica_hash_map.keys())
    to_delete = replica_file_set - source_file_set
    for file in to_delete:
        delete_files(f"{replica_folder_path}/{replica_hash_map[file]}")
        logger.info(f"File {replica_hash_map[file]} deleted")

    for hash, file_name in source_hash_map.items():
        # hash found
        if hash in replica_hash_map and file_name == replica_hash_map[hash]:
            continue
        elif hash in replica_hash_map and file_name != replica_hash_map[hash]:
            copy_files(
                f"{source_folder_path}/{file_name}",
                f"{replica_folder_path}/{file_name}",
            )
        # hash not found
        else:
            copy_files(
                f"{source_folder_path}/{file_name}",
                f"{replica_folder_path}/{file_name}",
            )


if __name__ == "__main__":
    run()
