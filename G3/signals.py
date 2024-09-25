"""
File location; .../G3/signals.py
Description: This file contains all the signals for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

# Application imports
from G3.models import G3Data, G3Results
from G3.utils import (
    upd_proc_data,
    upd_g3results,
    upd_g3simulparams,
)
from . import logger

# ------------------------------------------
# Signals for the G3 app.
# ------------------------------------------


@receiver(post_save, sender=G3Data)
def G3Data_post_save(sender, instance, created, **kwargs):
    """
    This signal is triggered after a new G3Data instance is saved.
    """

    # After the instance is saved, update the G3Results instance
    upd_g3results(instance=instance, deleted=False)
    # Then update the G3SimulParams instance
    upd_g3simulparams(instance=instance, deleted=False)

    if created:
        # If a new instance is created, log the instance ID
        logger.info(f"New {sender} instance CREATED with id: {instance.id}")
    else:
        # If an existing instance is updated, log the instance ID
        logger.info(f"{sender} instance UPDATED with id: {instance.id}")


@receiver(post_delete, sender=G3Data)
def G3Data_post_delete(sender, instance, **kwargs):
    """
    This signal is triggered after a G3Data instance is deleted.
    """

    # After the instance is DELETED, update the G3Results instance accordingly.
    upd_g3results(instance=instance, deleted=True)
    # Then update the G3SimulParams instance.
    # upd_g3simulparams(instance=instance, deleted=True)
    # Finally, log the deletion of the instance ID in the log file.
    logger.info(f"{sender} instance DELETED with id: {instance.id}")


@receiver(pre_save, sender=G3Data)
def G3Data_pre_save(sender, instance, **kwargs):
    """
    This signal is triggered before a G3Data instance is saved.
    """

    # Before the instance is saved, update the proc_data with the new raw_data.
    upd_proc_data(instance=instance, sender=sender)
