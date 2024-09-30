from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os

class DataController(BaseController):
  def __init__(self):
      super().__init__()
      # تحويل الحجم من ميغابايت إلى بايت
      self.size_scale = 1048576 

  # دالة للتحقق من صحة الملف المحمل
  def vaildate_upload_file(self, file: UploadFile):
      # التحقق من نوع الملف
      if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
          return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED
      
      # التحقق من حجم الملف
      if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
          return False, ResponseSignal.FILE_SIZE_EXCEEDED

      # إذا كان الملف صالحًا
      return True, ResponseSignal.FILE_UPLOAD_SUCCESS

  # دالة لتوليد اسم ملف فريد
  def generate_unique_filepath(self, orig_file_name: str, project_id: str):
      # توليد مفتاح عشوائي
      random_key = self.generate_random_string()
      # الحصول على مسار المشروع
      project_path = ProjectController().get_project_path(project_id=project_id)

      # تنظيف اسم الملف الأصلي
      cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)
      # إنشاء مسار جديد للملف
      new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

      # التحقق من عدم وجود الملف بنفس الاسم
      while os.path.exists(new_file_path):
          random_key = self.generate_random_string()
          new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

      return new_file_path, random_key + "_" + cleaned_file_name 

  # دالة لتنظيف اسم الملف
  def get_clean_file_name(self, orig_file_name: str):
      # إزالة الأحرف غير المرغوب فيها
      cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())
      # استبدال المسافات بشرطة سفلية
      cleaned_file_name = cleaned_file_name.replace(" ", "_")

      return cleaned_file_name