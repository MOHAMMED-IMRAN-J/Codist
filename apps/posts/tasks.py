from celery import shared_task
import cloudinary.uploader

@shared_task
def upload_video_task(file_content, filename):
    """
    Since we can't easily pass InMemoryUploadedFile to celery,
    we pass the raw content or save to generic temp format and pass path.
    For Cloudinary, the uploader can accept raw bytes.
    """
    response = cloudinary.uploader.upload(
        file_content,
        folder='codist/videos',
        resource_type='video',
        eager=[{'format': 'mp4', 'quality': 'auto'}],
        eager_async=True
    )
    video_url = response.get('secure_url')
    thumbnail_url = video_url.replace('/upload/', '/upload/so_0/') if video_url else None
    
    return {
        'status': 'complete',
        'video_url': video_url,
        'thumbnail_url': thumbnail_url,
        'duration': response.get('duration', 0.0)
    }
