"""
File location; .../G1/signals.py
Description: This file contains all the signals for the G1 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Global imports
from . import logger

# Django imports
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

# Application imports
from G1.models import G1Data
from G1.utils import upd_proc_data, upd_g1results

# ------------------------------------------
# Signals for the G1 app.
# ------------------------------------------


@receiver(post_save, sender=G1Data)
def G1Data_post_save(sender, instance, created, **kwargs):
    """
    This signal is triggered after a new G3Data instance is saved.
    """

    # After the instance is saved, update the g1results model instance.
    upd_proc_data(instance=instance, sender=sender)
    # Then, update the g1results instance.
    upd_g1results(instance=instance, deleted=False)

    if created:
        # If a new instance is created, log the instance ID
        logger.info(f"New {sender} instance CREATED with id: {instance.id}")
    else:
        # If an existing instance is updated, log the instance ID
        logger.info(f"{sender} instance UPDATED with id: {instance.id}")


@receiver(post_delete, sender=G1Data)
def G1Data_post_delete(sender, instance, **kwargs):
    """
    This signal is triggered after a G1Data instance is deleted.
    """

    # After the instance is DELETED, update the g1results instance.
    upd_g1results(instance=instance, deleted=True)

    # Log the deletion of the instance ID in the log file.
    logger.info(f"{sender} instance DELETED with id: {instance.id}")


@receiver(pre_save, sender=G1Data)
def G1Data_pre_save(sender, instance, **kwargs):
    """
    This signal is triggered before a G1Data instance is saved.
    """
