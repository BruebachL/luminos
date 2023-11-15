class AbstractManagedObject(object):

    def __init__(self, file_hash, file_path, **kwargs):
        self.file_hash = file_hash
        self.file_path = file_path
        self.kwargs = kwargs