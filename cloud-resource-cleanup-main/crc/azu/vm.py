import datetime
import logging
import time
from typing import Dict, List

from crc.azu._base import Base
from crc.service import Service


class VM(Service):
    

    default_instance_state = ["running"]
  

    def __init__(
        self,
        dry_run: bool,
        filter_tags: Dict[str, List[str]],
        exception_tags: Dict[str, List[str]],
        age: Dict[str, int],
        notags: Dict[str, List[str]],
    ) -> None:
        
        super().__init__()
        self.instance_names_to_delete = []
        self.instance_names_to_stop = []
        self.nics_names_to_delete = []
        self.base = Base()
        self.dry_run = dry_run
        self.filter_tags = filter_tags
        self.exception_tags = exception_tags
        self.age = age
        self.notags = notags

    @property
    def get_deleted(self):
        
        return self.instance_names_to_delete

    @property
    def delete_count(self):
        
        count = len(self.instance_names_to_delete)
        logging.info(f"count of items in instance_names_to_delete: {count}")
        return count

    @property
    def get_deleted_nic(self):
        return self.nics_names_to_delete

    @property
    def nic_delete_count(self):
        count = len(self.nics_names_to_delete)
        logging.info(f"count of items in nics_names_to_delete: {count}")
        return count

    @property
    def get_stopped(self):
        return self.instance_names_to_stop

    @property
    def stopped_count(self):
        count = len(self.instance_names_to_stop)
        logging.info(f"count of items in instance_names_to_stop: {count}")
        return count

    def _perform_operation(
        self,
        operation_type: str,
        instance_state: List[str] = default_instance_state,
    ) -> None:
        

        vms = self.base.get_compute_client().virtual_machines.list_all()

        for vm in vms:
            if self._should_perform_operation_on_vm(vm):
                dt = datetime.datetime.now().astimezone(vm.time_created.tzinfo)

                if self.is_old(self.age, dt, vm.time_created):
                    try:
                        status = self._get_vm_status(vm.name)

                        if any(state in status for state in instance_state):
                            if operation_type == "delete":
                                self._delete_vm(vm.name)
                            elif operation_type == "stop":
                                self._stop_vm(vm.name)
                    except Exception as e:
                        logging.error(
                            f"Error occurred while processing {vm.name} instance: {e}"
                        )

        # Using more descriptive if conditions
        if not self.instance_names_to_delete and not self.instance_names_to_stop:
            logging.warning(f"No Azure instances to {operation_type}.")

        if operation_type == "delete":
            if not self.dry_run:
                logging.warning(
                    f"number of Azure instances deleted: {len(self.instance_names_to_delete)}"
                )
                logging.warning(
                    f"List of Azure instances deleted: {self.instance_names_to_delete}"
                )
                logging.warning(
                    f"number of Azure nics deleted: {len(self.nics_names_to_delete)}"
                )
                logging.warning(
                    f"List of Azure nics deleted: {self.nics_names_to_delete}"
                )
            else:
                logging.warning(
                    f"List of Azure instances (Total: {len(self.instance_names_to_delete)}) which will be deleted: {self.instance_names_to_delete}"
                )
                logging.warning(
                    f"List of Azure nics (Total: {len(self.nics_names_to_delete)}) which will be deleted: {self.nics_names_to_delete}"
                )

        if operation_type == "stop":
            if not self.dry_run:
                logging.warning(
                    f"number of Azure instances stopped: {len(self.instance_names_to_stop)}"
                )
                logging.warning(
                    f"List of Azure instances stopped: {self.instance_names_to_stop}"
                )
            else:
                logging.warning(
                    f"List of Azure instances (Total: {len(self.instance_names_to_stop)}) which will be stopped: {self.instance_names_to_stop}"
                )

    def _should_perform_operation_on_vm(self, vm) -> bool:
        
        if not vm.tags:
            return False

        if self._should_skip_instance(vm):
            return False

        if not self.filter_tags or any(
            key in vm.tags and (not value or vm.tags[key] in value)
            for key, value in self.filter_tags.items()
        ):
            return True
        return False

    def _should_skip_instance(self, vm):
        in_exception_tags = False
        in_no_tags = False
        if self.exception_tags:
            in_exception_tags = any(
                key in vm.tags and (not value or vm.tags[key] in value)
                for key, value in self.exception_tags.items()
            )
            if in_exception_tags:
                return True
        if self.notags:
            in_no_tags = all(
                key in vm.tags and (not value or vm.tags[key] in value)
                for key, value in self.notags.items()
            )
        return in_no_tags

    def _get_vm_status(self, vm_name: str) -> str:
       
        return (
            self.base.get_compute_client()
            .virtual_machines.instance_view(self.base.resource_group, vm_name)
            .statuses[1]
            .display_status
        )

    def _delete_vm(self, vm_name: str):
        if not self.dry_run:
            self.base.get_compute_client().virtual_machines.begin_delete(
                self.base.resource_group, vm_name
            )
            logging.info("Deleting virtual machine: %s", vm_name)
        self.instance_names_to_delete.append(vm_name)
        self._delete_nic(vm_name)

    def _stop_vm(self, vm_name: str):
        if not self.dry_run:
            self.base.get_compute_client().virtual_machines.begin_power_off(
                self.base.resource_group, vm_name
            )
            logging.info("Stopping virtual machine: %s", vm_name)
        self.instance_names_to_stop.append(vm_name)

    def delete(
        self,
        instance_state: List[str] = default_instance_state,
    ) -> None:
        self._perform_operation("delete", instance_state)

    def stop(self) -> None:
        self._perform_operation("stop", self.default_instance_state)

    def _delete_nic(self, vm_name):
        deleted_nic = False
        failure_count = 3
        nic_name = f"{vm_name}-NIC"
        while not deleted_nic and failure_count:
            try:
                if not self.dry_run:
                    logging.info(
                        f"Sleeping for {60*failure_count} seconds before deleting NIC"
                    )
                    time.sleep(60 * failure_count)  # Sleeping for 180 seconds
                    self.base.get_network_client().network_interfaces.begin_delete(
                        self.base.resource_group, nic_name
                    )
                    logging.info(f"Deleted the NIC - {nic_name}")
                deleted_nic = True
                self.nics_names_to_delete.append(nic_name)
            except Exception as e:
                failure_count -= 1
                logging.error(f"Error occurred while processing {nic_name} NIC: {e}")
                if failure_count:
                    logging.info(f"Retrying Deletion of NIC {nic_name}")

        if not failure_count:
            logging.error(f"Failed to delete the NIC - {nic_name}")
