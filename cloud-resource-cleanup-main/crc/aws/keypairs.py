import datetime
import logging
import re
from typing import Dict, List

import boto3

from crc.aws._base import get_all_regions
from crc.service import Service


class KeyPairs(Service):
    

    service_name = "ec2"
    """
    The service_name variable specifies the AWS service that this class will interact with.
    """

    default_region_name = "us-west-2"
    """
    The default_region_name variable specifies the default region to be used when interacting with the AWS service.
    """

    def __init__(
        self,
        dry_run: bool,
        name_regex: List[str],
        exception_regex: List[str],
        age: Dict[str, int],
    ) -> None:
       
        super().__init__()
        self.deleted_keypairs = []
        self.dry_run = dry_run
        self.name_regex = name_regex
        self.exception_regex = exception_regex
        self.age = age

    @property
    def get_deleted(self):
        
        return self.deleted_keypairs

    @property
    def count(self):
       
        count = len(self.deleted_keypairs)
        logging.info(f"count of items in deleted_keypairs: {count}")
        return count

    def delete(self):
        
        if self.exception_regex:
            exception_regex = set(self.exception_regex)
        else:
            exception_regex = set()
        for region in get_all_regions(self.service_name, self.default_region_name):
            keypairs_to_delete = set()
            client = boto3.client(self.service_name, region_name=region)
            keypairs = client.describe_key_pairs()
            for keypair in keypairs["KeyPairs"]:
                if "KeyName" not in keypair or "CreateTime" not in keypair:
                    continue
                keypair_name = keypair["KeyName"]
                keypair_create_time = keypair["CreateTime"]
                dt = datetime.datetime.now().astimezone(keypair_create_time.tzinfo)

                # Check if keypair name matches specified regex
                match_name_regex = not self.name_regex or any(
                    re.search(kpn, keypair_name) for kpn in self.name_regex
                )
                match_exception_regex = self.exception_regex and any(
                    re.search(kpn, keypair_name) for kpn in exception_regex
                )

                if match_name_regex and not match_exception_regex:
                    if self.is_old(
                        self.age,
                        dt,
                        keypair_create_time,
                    ):
                        keypairs_to_delete.add(keypair_name)
                    else:
                        logging.info(
                            f"Keypair {keypair_name} is not old enough to be deleted."
                        )
                else:
                    if match_exception_regex:
                        logging.info(
                            f"Keypair {keypair_name} is in exception_regex {self.exception_regex}."
                        )

            for keypair_to_delete in keypairs_to_delete:
                if not self.dry_run:
                    response = client.delete_key_pair(KeyName=keypair_to_delete)
                    logging.info(
                        f"Deleted keypair: {keypair_to_delete} with response: {response}"
                    )
                self.deleted_keypairs.append(keypair_to_delete)

        if not self.dry_run:
            logging.warning(
                f"number of AWS keypairs deleted: {len(self.deleted_keypairs)}"
            )
            logging.warning(f"List of AWS keypairs deleted: {self.deleted_keypairs}")
        else:
            logging.warning(
                f"List of AWS keypairs (Total: {len(self.deleted_keypairs)}) which will be deleted: {self.deleted_keypairs}"
            )
