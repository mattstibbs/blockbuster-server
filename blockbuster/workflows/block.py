# WORK IN PROGRESS

import bb_dbconnector_factory


class BlockRequest:

    def __init__(self, blocker_number, blocked_reg):
        self.blocker_number = blocker_number
        self.blocked_reg = blocked_reg


class BlockRequestProcessor:

    def __init__(self):
        pass

    # PARAMETER: BlockRequest object
    # RETURNS: Errorcode int
    # This method takes a BlockRequest and processes the block returning the status of the BlockRequest when complete.
    @staticmethod
    def process_block_request(self, block_request):

        success = True

        # If the BlockRequest has been processed successfully, the method should return an error code of 0
        if success:
            return 0

        # If there was an exception trying to process the BlockRequest, the method should return -1
        else:
            return -1