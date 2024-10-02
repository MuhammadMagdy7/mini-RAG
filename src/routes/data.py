from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import os
from models import ResponseSignal
import aiofiles
import logging 
from .schemes.data import ProcessRequest
from fastapi import HTTPException
from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunk
from models.ChunkModel import ChunkModel

# إعداد نظام تسجيل الأخطاء
logger = logging.getLogger('uvicorn.error')

# إنشاء مسار API جديد للتعامل مع البيانات
data_router = APIRouter(
  prefix="/api/v1/data", 
  tags=["api_v1", "data"]
)

# تعريف دالة لتحميل البيانات
@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                    app_settings: Settings = Depends(get_settings)):

    project_model = ProjectModel(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    # التحقق من خصائص الملف
    data_controller = DataController()
    is_valid, result_signal = data_controller.vaildate_upload_file(file=file)

    # إذا كان الملف غير صالح، إرجاع استجابة خطأ
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Signal": result_signal}
        )

    # الحصول على مسار المشروع باستخدام معرف المشروع
    project_dir_path = ProjectController().get_project_path(project_id=project_id)

    # إنشاء اسم ملف فريد
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        # فتح الملف للكتابة بشكل غير متزامن
        async with aiofiles.open(file_path, "wb") as f:
            # قراءة وكتابة الملف على شكل قطع
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        # تسجيل الخطأ في حالة حدوث مشكلة أثناء التحميل
        logger.error(f"Error while uploading file: {e}")

        # إرجاع استجابة خطأ
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Signal": ResponseSignal.FILE_UPLOAD_FAILED.value}
        )

    # إرجاع استجابة نجاح عند اكتمال التحميل
    return JSONResponse(
        content={
            "Signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": file_id,
        }
    )



@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id:str, procss_request: ProcessRequest):

    file_id = procss_request.file_id
    chunk_size = procss_request.chunk_size
    overlap_size = procss_request.overlap_size
    do_reset = procss_request.do_reset

    project_model = ProjectModel(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)





    procss_controller = ProcessController(project_id=project_id)
    file_content = procss_controller.get_file_content(file_id=file_id)

    file_chunks = procss_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size

    )

    if file_chunks is None or len(file_chunks) == 0 :
        return JSONResponse(
          status_code=status.HTTP_400_BAD_REQUEST,
          content={"Signal": ResponseSignal.PROCESSING_FAILED.value}
      )

    file_chunks_records = [
    DataChunk(
        chunk_text= chunk.page_content,
        chunk_metadata= chunk.metadata,
        chunk_order=i+1,
        chunk_project_id=project.id
    )
    for i, chunk in enumerate(file_chunks)
    ]


    chunk_model = ChunkModel(
        db_client=request.app.db_client
    )

    if do_reset == 1 :
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )


    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(    
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )
