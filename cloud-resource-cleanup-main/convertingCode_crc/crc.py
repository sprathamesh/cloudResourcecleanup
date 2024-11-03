import argparse
import ast
import os
from typing import Dict, List

from crc.azu.disk import Disk
from crc.azu.ip import IP as AZU_IP
from crc.azu.vm import VM as AZU_VM

# List of supported clouds and resources
CLOUDS = ["aws"]
RESOURCES = ["disk", "ip", "keypair", "vm"]

DELETED = "Deleted"
STOPPED = "Stopped"

NICS = "NIC"
DISKS = "Disk"
VMS = "VM"
IPS = "IP"
KEYPAIRS = "Keypair"


class CRC:
    def __init__(
        self,
        cloud: str,
        dry_run: bool,
        notags: dict,
    ) -> None:
        self.cloud = cloud
        self.dry_run = dry_run
        self.notags = notags
       

    def _delete_vm(self, vm, instance_state: List[str]):
        if not instance_state:
            vm.delete()
        else:
            vm.delete(instance_state)

    def _get_vm(
        self,
        filter_tags: Dict[str, List[str]],
        exception_tags: Dict[str, List[str]],
        age: Dict[str, int],
    ):
        if self.cloud == "azure":
            return AZU_VM(self.dry_run, filter_tags, exception_tags, age, self.notags)
        raise ValueError(
            f"Invalid cloud provided: {self.cloud}. Supported clouds are {CLOUDS}"
        )

    def _get_ip(
        self,
        filter_tags: Dict[str, List[str]],
        exception_tags: Dict[str, List[str]],
        name_regex: List[str],
        exception_regex: List[str],
    ):
        if self.cloud == "azure":
            return AZU_IP(self.dry_run, filter_tags, exception_tags, self.notags)
        raise ValueError(
            f"Invalid cloud provided: {self.cloud}. Supported clouds are {CLOUDS}"
        )

    def get_msg(
        self, resource: str, operation_type: str, operated_list: List[str]
    ) -> str:
        operated_list_length = len(operated_list)

        if self.dry_run:
            return f"`Dry Run`: Will be {operation_type}: `{operated_list_length}` {self.cloud} {resource}(s):\n`{operated_list}`"

        return f"{operation_type} the following `{operated_list_length}` {self.cloud} {resource}(s):\n`{operated_list}`"
    
    def delete_vm(
        self,
        filter_tags: Dict[str, List[str]],
        exception_tags: Dict[str, List[str]],
        age: Dict[str, int],
        instance_state: List[str],
    ):
        vm = self._get_vm(filter_tags, exception_tags, age)
        self._delete_vm(vm, instance_state)

    def stop_vm(
        self,
        filter_tags: Dict[str, List[str]],
        exception_tags: Dict[str, List[str]],
        age: Dict[str, int],
    ):
        vm = self._get_vm(filter_tags, exception_tags, age)
        vm.stop()


    def delete_ip(
        self,
        filter_tags: Dict[str, List[str]],
        exception_tags: Dict[str, List[str]],
        name_regex: List[str],
        exception_regex: List[str],
    ):
        ip = self._get_ip(
            filter_tags,
            exception_tags,
            name_regex,
            exception_regex,
        )
        ip.delete()

    def delete_disks(
        self,
        filter_tags: Dict[str, List[str]],
        exception_tags: Dict[str, List[str]],
        age: Dict[str, int],
    ):
        if self.cloud != "azure":
            raise ValueError(
                "Incorrect Cloud Provided. Disks operation is supported only on AZURE. AWS, GCP clean the NICs, Disks along with VM"
            )

        disk = Disk(self.dry_run, filter_tags, exception_tags, age, self.notags)
        disk.delete()



def get_argparser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Cleanup Resources across different clouds",
    )

    # Add Argument for Cloud
    parser.add_argument(
        "-c",
        "--cloud",
        choices=["aws", "azure", "gcp", "all"],
        required=True,
        metavar="CLOUD",
        help="The cloud to operate on. Valid options are: 'aws', 'azure', 'gcp', 'all'. Example: -c or --cloud all",
    )

    # Add Argument for Resource Type
    parser.add_argument(
        "-r",
        "--resource",
        default="all",
        choices=["disk", "ip", "keypair", "vm", "all"],
        metavar="RESOURCE",
        help="Type of resource to operate on. Valid options are: 'disk', 'ip', 'keypair', 'vm', 'all'. Default: 'all'. Example: -r or --resource vm",
    )

    # Add Argument for Operation Type
    parser.add_argument(
        "-o",
        "--operation_type",
        default="delete",
        choices=["delete", "stop"],
        metavar="OPERATION",
        help="Type of operation to perform on resource. Valid options are: 'delete', 'stop'. Default: 'delete'. Example: -o or --operation_type stop",
    )

    # Add argument for resource states
    parser.add_argument(
        "-s",
        "--resource_states",
        type=ast.literal_eval,
        metavar="['state1', 'state2']",
        help="State of the resource to filter. Example: --resource_states ['RUNNING', 'STOPPED']",
    )

    # Add argument for filter tags
    parser.add_argument(
        "-f",
        "--filter_tags",
        type=ast.literal_eval,
        metavar="{key1: [value1, value2], key2: [value3, value4]}",
        help="Tags to use for filtering resources. Example: --filter_tags {'test_task': ['test', 'stress-test']}",
    )

    # Add argument for exception tags
    parser.add_argument(
        "-e",
        "--exception_tags",
        type=ast.literal_eval,
        metavar="{key1: [value1, value2], key2: [value3, value4]}",
        help="Exception tags to use for filtering resources. Example: --exception_tags {'test_task': ['test-keep-resources', 'stress-test-keep-resources']}",
    )

    # Add Argument for Age Threshold
    parser.add_argument(
        "-a",
        "--age",
        type=ast.literal_eval,
        metavar="{'days': 3, 'hours': 12}",
        help="Age Threshold for resources. Age is not respected for IPs. Example: -a or --age {'days': 3, 'hours': 12}",
    )

    # Add Argument for Dry Run Mode
    parser.add_argument(
        "-d",
        "--dry_run",
        action="store_true",
        help="Enable dry_run only mode",
    )

    # Add Argument for Tag not present
    parser.add_argument(
        "-t",
        "--notags",
        type=ast.literal_eval,
        help="Filter by Tags not Present. Leave value of Key empty to indicate 'any' value. Format: -t or --notags {'test_task': ['test'], 'test_owner': []}",
        metavar="{key1: [value1, value2], key2: [value3, value4]}",
    )
    
def is_valid_type(name: str, value, expected_type):
    if not isinstance(value, expected_type):
        raise ValueError(
            f"{name} should be of type {expected_type}, but got {type(value)}"
        )


def is_valid_list(name: str, value):
    if value is not None:
        is_valid_type(name, value, list)


def is_valid_dict(name: str, value):
    if value is not None:
        is_valid_type(name, value, dict)


def are_values_of_dict_lists(name: str, value):
    if value is not None:
        is_valid_dict(name, value)
        for key, val in value.items():
            is_valid_list(f"Value of {name} with key {key}", val)

def main():
    args = get_argparser()
    clouds = args.get("cloud")
    resources = args.get("resource")
    operation_type = args.get("operation_type")
    resource_states = args.get("resource_states")
    filter_tags = args.get("filter_tags")
    age = args.get("age")
    dry_run = args.get("dry_run")
    notags = args.get("notags")
    
    # Validate operation_type and resources
    if operation_type == "stop" and resources != "vm":
        raise ValueError("Stop is supported only for vm resource")

    # Validate resources and clouds
    if resources == "all" and clouds != "all":
        raise ValueError(
            "All Resources cleanup is supported only with all Clouds. Format: --cloud all --resources all"
        )

    # Process Cloud
    clouds = CLOUDS if clouds == "all" else [clouds]

    # Process Resources
    resources = RESOURCES if resources == "all" else [resources]

    # Validate Input Values
    is_valid_list("resource_states", resource_states)
    are_values_of_dict_lists("filter_tags", filter_tags)
    is_valid_dict("age", age)

    # Perform operations
    for cloud in clouds:
        crc = CRC(
            cloud,
            dry_run,
            notags,
        )
        for resource in resources:
            if resource == "disk":
                crc.delete_disks(filter_tags,  age)
            elif resource == "ip":
                crc.delete_ip(
                    filter_tags,
                )
            elif resource == "vm":
                if operation_type == "delete":
                    crc.delete_vm(
                        filter_tags,
                        age,
                        resource_states,
                    )
                elif operation_type == "stop":
                    crc.stop_vm(filter_tags, age)


if __name__ == "__main__":
    main()
