from django.db.models.fields.files import FileField, FieldFile
import pdb

class WizcardQueuedFieldFile(FieldFile):
    def __init__(self, *args, **kwargs):
        super(WizcardQueuedFieldFile, self).__init__(*args, **kwargs)

    def transfer(self):
        """
        Transfers the file using the storage backend. taken from 
        QueuedFileField
        """
        return self.storage.transfer(self.name)

    def remote_url(self):
        return self.storage.remote.url(self.name)

    def local_path(self):
        return self.storage.local.path(self.name)

class WizcardQueuedFileField(FileField):
    attr_class = WizcardQueuedFieldFile
