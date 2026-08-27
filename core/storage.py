import cloudinary.uploader
from django.conf import settings

def upload_image(file, folder='codist/images'):
    response = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type='image',
        fetch_format='auto',
        quality='auto'
    )
    return response.get('secure_url')

def upload_video_async(file, folder='codist/videos'):
    response = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type='video',
        eager=[{'format': 'mp4', 'quality': 'auto'}],
        eager_async=True
    )
    video_url = response.get('secure_url')
    # Thumbnail URL by replacing '/upload/' with '/upload/so_0/'
    thumbnail_url = video_url.replace('/upload/', '/upload/so_0/') if video_url else None
    return {
        'video_url': video_url,
        'thumbnail_url': thumbnail_url,
        # Duration is returned if immediately available, or we might need it via cloudinary API later, but standard upload usually returns native metadata
        'duration': response.get('duration', 0.0)
    }

def upload_repo_file(file, folder='codist/repos'):
    response = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type='raw'
    )
    return response.get('secure_url')
