from queued_storage.backends import QueuedS3BotoStorage

class WizcardQueuedS3BotoStorage(QueuedS3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(WizcardQueuedS3BotoStorage, self).__init__(*args, **kwargs)
