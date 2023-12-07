from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from user.middleware import api_key_required
from django.contrib.sites.shortcuts import get_current_site


from .throttles import AuthenticatedUserThrottle, AnonymousUserThrottle
from rest_framework.permissions import AllowAny


from user.models import *

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from user.middleware import authenticate_with_token_or_api_key


from django.http import JsonResponse
from PIL import Image , UnidentifiedImageError, ExifTags
import piexif
import os
from django.http import HttpResponse

from tempfile import NamedTemporaryFile

from django.views.decorators.csrf import csrf_exempt




import cv2
import numpy as np

import rembg
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt




def get_exif_info(image_path):
    try:
        with open(image_path, 'rb') as file:
            img = Image.open(file)
            exif_dict = piexif.load(img.info.get('exif', b''))
    except (FileNotFoundError, UnidentifiedImageError):
        exif_dict = {}

    make_model = exif_dict.get('0th', {}).get(piexif.ImageIFD.Make, b'').decode('utf-8', errors='replace')
    model = exif_dict.get('0th', {}).get(piexif.ImageIFD.Model, b'').decode('utf-8', errors='replace')
    date_time = exif_dict.get(piexif.ExifIFD.DateTimeOriginal, b'').decode('utf-8', errors='replace')
    resolution = exif_dict.get(piexif.ImageIFD.XResolution, (0, 0))

    return {
        'make_model': make_model,
        'model': model,
        'date_time': date_time,
        'resolution': resolution,
        
    }
    


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
@csrf_exempt
@throttle_classes([AuthenticatedUserThrottle])
@authenticate_with_token_or_api_key
def upload_image_authenticate(request):
    if request.method == 'POST':
        try:
            # Use request.FILES to access the uploaded file
            image = request.FILES['file']
        except KeyError:
            return JsonResponse({'error': 'Missing file in the request'}, status=status.HTTP_400_BAD_REQUEST)

        original_filename = image.name  # Access the name of the uploaded file
        image_dir = os.path.join(settings.BASE_DIR, 'media', 'received')

        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        image_path = os.path.join('received', f'received_{original_filename.replace(" ", "_")}')
        absolute_image_path = os.path.join(settings.BASE_DIR, 'media', image_path)

        with open(absolute_image_path, 'wb') as file:
            for chunk in image.chunks():
                file.write(chunk)

        # Get Exif information using the new function
        exif_info = get_exif_info(absolute_image_path)

        # Construct the full image URL with the domain
        current_site = get_current_site(request)
        domain = current_site.domain
        full_image_path = f"{domain}/{settings.MEDIA_URL}{image_path}"

        response_data = {
            'status': 'Image uploaded successfully',
            'image_path': full_image_path,
            'exif_data': exif_info,
        }

        return JsonResponse(response_data, status=status.HTTP_201_CREATED)

    return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@throttle_classes([AnonymousUserThrottle])
def upload_image_unauthenticate(request):
    if request.method == 'POST':
        try:
            # Use request.FILES to access the uploaded file
            image = request.FILES['file']
        except KeyError:
            return JsonResponse({'error': 'Missing file in the request'}, status=status.HTTP_400_BAD_REQUEST)

        original_filename = image.name  # Access the name of the uploaded file
        image_dir = os.path.join(settings.BASE_DIR, 'media', 'received')
        
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        image_path = os.path.join('received', f'received_{original_filename.replace(" ", "_")}')
        absolute_image_path = os.path.join(settings.BASE_DIR, 'media', image_path)

        with open(absolute_image_path, 'wb') as file:
            for chunk in image.chunks():
                file.write(chunk)

        # Get Exif information using the new function
        exif_info = get_exif_info(absolute_image_path)

        request.session['uploaded_image_path'] = absolute_image_path
        request.session['original_filename'] = original_filename

        response_data = {
            'status': 'Image uploaded successfully',
            'image_path': absolute_image_path,
            'exif_data': exif_info,
        }

        return JsonResponse(response_data, status=status.HTTP_201_CREATED)

    return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@csrf_exempt
@throttle_classes([AuthenticatedUserThrottle])
@authenticate_with_token_or_api_key
@permission_classes([AllowAny])
def resize_image(request):
    if request.method == 'POST':
        try:
            height = int(request.data['height'])
            width = int(request.data['width'])
            image_path = request.data['image_path']  # Add this line to get the image path from the request
        except (KeyError, ValueError):
            return Response({'error': 'Missing or invalid height/width parameters'}, status=status.HTTP_400_BAD_REQUEST)

        if not os.path.exists(image_path):
            return Response({'error': 'Invalid image path'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the 'resized' directory if it doesn't exist
            resized_dir = os.path.join(settings.BASE_DIR, 'media', 'resized')
            if not os.path.exists(resized_dir):
                os.makedirs(resized_dir)

            # Open the image
            with open(image_path, 'rb') as file:
                img = Image.open(file)

                # Resize the image
                resized_image = img.resize((width, height))

                # Save the resized image in the 'resized' folder
                resized_image_path = os.path.join(resized_dir, f'resized_{os.path.basename(image_path)}')
                resized_image.save(resized_image_path, 'JPEG')

            # Return a response with the resized image path
            return JsonResponse({'status': 'Image resized successfully', 'resized_image_path': resized_image_path})

        except (FileNotFoundError, UnidentifiedImageError):
            return Response({'error': 'Error resizing image'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)








@csrf_exempt
@throttle_classes([AuthenticatedUserThrottle])
@authenticate_with_token_or_api_key
@permission_classes([AllowAny])
def remove_background(request):
    image_path = request.session.get('uploaded_image_path')

    if not image_path or not os.path.exists(image_path):
        return JsonResponse({'error': 'No uploaded file found'}, status=400)

    try:
        # Create the 'background' directory if it doesn't exist
        background_dir = os.path.join(settings.BASE_DIR, 'media', 'background')
        if not os.path.exists(background_dir):
            os.makedirs(background_dir)

        with open(image_path, 'rb') as input_file:
            input_data = input_file.read()
            output_data = rembg.remove(input_data)

        # Save the image with a transparent background in the 'background' folder
        transparent_image_path = os.path.join(background_dir, f'transparent_{os.path.basename(image_path)}')
        with open(transparent_image_path, 'wb') as output_file:
            output_file.write(output_data)

        # Return the path to the transparent image in the response
        return JsonResponse({'transparent_image_path': transparent_image_path})

    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)







def add_shadows(request):
    # Assuming the uploaded image path is stored in the session
    image_path = request.session.get('uploaded_image_path')

    if not image_path or not os.path.exists(image_path):
        return JsonResponse({'error': 'No uploaded file found'}, status=400)

    try:
        # Read the original image
        img = cv2.imread(image_path)

        if img is None:
            return JsonResponse({'error': 'Failed to read the image'}, status=500)

        # Create a mask for the shadow
        mask = np.zeros_like(img)

        # Define the shadow color (you can adjust these values)
        shadow_color = (50, 50, 50)

        # Specify the position and size of the shadow
        shadow_position = (50, 50)
        shadow_size = (100, 100)

        # Add the shadow to the mask
        cv2.rectangle(mask, shadow_position, (shadow_position[0] + shadow_size[0], shadow_position[1] + shadow_size[1]), shadow_color, thickness=cv2.FILLED)

        # Combine the original image and the shadow using bitwise addition
        img_with_shadow = cv2.addWeighted(img, 1, mask, 0.5, 0)

        # Save the image with added shadows
        image_with_shadow_path = f'image_with_shadow_{os.path.basename(image_path)}'
        cv2.imwrite(image_with_shadow_path, img_with_shadow)

        # Return the path to the image with shadows in the response
        return JsonResponse({'image_with_shadow_path': image_with_shadow_path})

    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)





# from django.views.decorators.csrf import csrf_exempt
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from DeOldify.visualize import get_image_colorizer
# from PIL import Image

# @csrf_exempt
# def colorize_image(request):
#     if request.method == 'POST':
#         try:
#             # Assume the uploaded image is in the 'image' field of the POST request
#             uploaded_image = request.FILES['image']

#             # Save the uploaded image to a temporary file
#             temp_image_path = default_storage.save('temp_image.jpg', ContentFile(uploaded_image.read()))

#             # Colorize the image using DeOldify
#             colorizer = get_image_colorizer(artistic=True)
#             colorized_image = colorizer.get_transformed_image(temp_image_path)

#             # Save the colorized image to a new file
#             colorized_image_path = default_storage.save('colorized_image.jpg', ContentFile(colorized_image.read()))

#             # Return the path to the colorized image in the response
#             return JsonResponse({'colorized_image_path': colorized_image_path})

#         except Exception as e:
#             return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=400)




