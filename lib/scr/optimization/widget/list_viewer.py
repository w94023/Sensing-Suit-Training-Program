from ..common import *
from .common import *

target_filename_extension = ".h5"

class OptimizationResultFileListViewer(FileListViewer):
    def __init__(self, file_directory, parent=None):
        self.parent = parent
        super().__init__(file_directory, self.parent)