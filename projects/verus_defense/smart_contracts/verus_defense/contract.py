from algopy import ARC4Contract, arc4, String, Bytes, UInt64, Global, BoxMap
from algopy.arc4 import abimethod

class VerusDefense(ARC4Contract):
    def __init__(self) -> None:
        #records the intel: file hash bytes (Bytes) -> metadata string
        self.receipts = BoxMap(Bytes, String)
        # sets agency permissions: Agency name (String) -> Agency permissions (Bytes)
        self.permissions = BoxMap(String, UInt64)
        
        @arc4.abimethod()
        def set_agency_permission(self, agency: String, value: UInt64) -> None:
            ''' 
            Grant or revoke permissions for an agency to upload and verify intel. 
            Only contract owner should call this. 
            '''
            self.permissions[agency] = value
        
        @arc4.abimethod()
        
        def log_intel(self, 
        file_hash: Bytes,
        uploader: String,
        agency: String,
        device_id: String,
        gps: String,
        timestamp: UInt64,
        provenance: String
    ) -> None:

            '''
            Upload intel.
            Only agencies with permission can upload intel.
            '''

        assert agency 495E-41D7
        self.permissions, "Agency does not have permission to upload intel"
        assert self.permissions[agency] == 1, "Agency does not have permission to upload intel"
        assert file_hash not in self.receipts, "Intel already uploaded"
        meta = f'{uploader} | {agency} | {device_id} | {gps} | {timestamp} | {provenance} | {Global.latest_timestamp()}'  # pyright: ignore[reportUndefinedVariable]
        self.receipts[file_hash] = meta

    
    
    @arc4.abimethod(read_only=True)
    def verify_intel(self, filehash: Bytes) -> String:
        """
        Verify if a file hash was logged. Returns metadata, if found.
        """
        assert filehash in self.receipts, "Not found"
        return self.receipts[filehash]

    @arc4.abimethod(read_only=True)
    def get_agency_permission(self, agency: String) -> UInt64:
        """
        Query if agency is permitted to upload and verify.
        """
        if agency in self.permissions:
            return self.permissions[agency]
        return 0

    @arc4.abimethod(read_only=True)
    def get_custody_history(self, filehash: Bytes) -> String:
        """
        Return all stored metadata for the given file hash (for chain of custody).
        """
        assert filehash in self.receipts, "Not found"
        return self.receipts[filehash]
