import logging

import algokit_utils

logger = logging.getLogger(__name__)


# define deployment behaviour based on supplied app spec
def deploy() -> None:
    from smart_contracts.artifacts.verus_defense.verus_defense_client import (
        VerusDefenseFactory,
        SetAgencyPermissionArgs,
        LogIntelArgs,
        VerifyIntelArgs,
        GetAgencyPermissionArgs,
        GetCustodyHistoryArgs,
    )

    algorand = algokit_utils.AlgorandClient.from_environment()
    deployer_ = algorand.account.from_environment("DEPLOYER")

    factory = algorand.client.get_typed_app_factory(
        VerusDefenseFactory, default_sender=deployer_.address
    )

    app_client, result = factory.deploy(
        on_update=algokit_utils.OnUpdate.AppendApp,
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
    )

    if result.operation_performed in [
        algokit_utils.OperationPerformed.Create,
        algokit_utils.OperationPerformed.Replace,
    ]:
        algorand.send.payment(
            algokit_utils.PaymentParams(
                amount=algokit_utils.AlgoAmount(algo=1),
                sender=deployer_.address,
                receiver=app_client.app_address,
            )
        )

    # Sample flow matching VerusDefense contract methods
    agency_name = "DefenseAgency"
    logger.info("Granting upload permission to agency: %s", agency_name)
    app_client.send.set_agency_permission(
        args=SetAgencyPermissionArgs(agency=agency_name, value=1)
    )

    # Example intel
    file_hash = bytes.fromhex(
        "3d7f1e3a8b9c4d2f1a0b5c6d7e8f9a0b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f"
    )[:32]
    uploader = "field_agent_42"
    device_id = "device-12345"
    gps = "37.7749,-122.4194"
    timestamp = int(algokit_utils.get_current_timestamp())
    provenance = "drone"

    logger.info("Logging intel for file_hash: %s", file_hash.hex())
    app_client.send.log_intel(
        args=LogIntelArgs(
            file_hash=file_hash,
            uploader=uploader,
            agency=agency_name,
            device_id=device_id,
            gps=gps,
            timestamp=timestamp,
            provenance=provenance,
        )
    )

    logger.info("Verifying intel existence and reading metadata")
    verify_res = app_client.send.verify_intel(
        args=VerifyIntelArgs(filehash=file_hash)
    )
    logger.info("verify_intel => %s", verify_res.abi_return)

    logger.info("Checking agency permission")
    perm_res = app_client.send.get_agency_permission(
        args=GetAgencyPermissionArgs(agency=agency_name)
    )
    logger.info("get_agency_permission => %s", perm_res.abi_return)

    logger.info("Fetching custody history")
    custody_res = app_client.send.get_custody_history(
        args=GetCustodyHistoryArgs(filehash=file_hash)
    )
    logger.info("get_custody_history => %s", custody_res.abi_return)
