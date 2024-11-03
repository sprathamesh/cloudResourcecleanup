import logging
from typing import Dict, List

import boto3

from crc.aws._base import get_all_regions
from crc.service import Service


class ElasticIPs(Service):
   
    service_name = "ec2"
    """
    The service_name variable specifies the AWS service that this class will interact with.
    """

    default_region_name = "us-west-2"
    """
    The default_region_name variable specifies the default region to be used when interacting with the AWS service.
    """

    def __init__(
        self, dry_run: bool, filter_tags: dict, exception_tags: dict, notags: dict
    ) -> None:
        
        super().__init__()
        self.deleted_ips = []
        self.dry_run = dry_run
        self.filter_tags = filter_tags
        self.exception_tags = exception_tags
        self.notags = notags

    @property
    def get_deleted(self) -> str:
        
        return self.deleted_ips

    @property
    def count(self) -> int:
        
        count = len(self.deleted_ips)
        logging.info(f"count of items in deleted_ips: {count}")
        return count

    def _should_skip_instance(self, tags: List[Dict[str, str]]) -> bool:
        
        if not self.exception_tags and not self.notags:
            return False
        in_exception_tags = False
        in_no_tags = False
        for tag in tags:
            key = tag["Key"]
            if self.exception_tags:
                in_exception_tags = key in self.exception_tags and (
                    not self.exception_tags[key]
                    or tag["Value"] in self.exception_tags[key]
                )
                if in_exception_tags:
                    return True
            if self.notags:
                in_no_tags = all(
                    in_no_tags
                    and key in self.notags
                    and (not self.notags[key] or tag["Value"] in self.notags[key]),
                )

        return in_no_tags

    def delete(self):
       
        regions = get_all_regions(self.service_name, self.default_region_name)

        for region in regions:
            eips_to_delete = {}
            client = boto3.client(self.service_name, region_name=region)
            addresses = client.describe_addresses()["Addresses"]
            for eip in addresses:
                if "NetworkInterfaceId" not in eip and "Tags" in eip:
                    tags = eip["Tags"]
                    if self._should_skip_instance(tags):
                        continue
                    if not self.filter_tags:
                        eips_to_delete[eip["PublicIp"]] = eip["AllocationId"]
                        continue
                    for tag in tags:
                        key = tag["Key"]
                        # check for filter_tags match
                        if key in self.filter_tags and (
                            not self.filter_tags[key]
                            or tag["Value"] in self.filter_tags[key]
                        ):
                            eips_to_delete[eip["PublicIp"]] = eip["AllocationId"]

            if not self.dry_run:
                for ip in eips_to_delete:
                    client.release_address(AllocationId=eips_to_delete[ip])
                    logging.info(f"Deleted IP: {ip}")

            # Add deleted IPs to deleted_ips list
            self.deleted_ips.extend(list(eips_to_delete.keys()))

        if not self.dry_run:
            logging.warning(
                f"number of AWS Elastic IPs deleted: {len(self.deleted_ips)}"
            )
            logging.warning(f"List of AWS Elastic IPs deleted: {self.deleted_ips}")
        else:
            logging.warning(
                f"List of AWS Elastic IPs (Total: {len(self.deleted_ips)}) which will be deleted: {self.deleted_ips}"
            )
