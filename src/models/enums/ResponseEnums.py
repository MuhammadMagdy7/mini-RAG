from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDTED_SUCCESS = "FILE_VALIDTED_SUCCESS"
    FILE_TYPE_NOT_SUPPORTED = "FILE_TYPE_NOT_SUPPORTED"
    FILE_SIZE_EXCEEDED = "VFILE_SIZE_EXCEEDED"
    FILE_UPLOAD_SUCCESS = "FILE_UPLOAD_SUCCESS"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_file_found_with_this_id"
