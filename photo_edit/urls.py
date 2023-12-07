from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', upload_image_authenticate),
    path('resize/', resize_image),
    # path('process-image/<int:image_id>/', process_image, name='process-image'),
    path('remove_background/', remove_background),
    path('shadow/', add_shadows),
]
