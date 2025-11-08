import os
import subprocess
import datetime
import boto3
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from cryptography.fernet import Fernet
from cores.models import BackupLog


def encrypt_file(filepath):
    """Encrypt file before uploading to S3."""
    fernet = Fernet(settings.FERNET_KEY)
    with open(filepath, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(filepath, "wb") as f:
        f.write(encrypted)


def backup_and_cleanup(auto=True):
    """Performs local + S3 backup and cleanup."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    filename = f"cbt_backup_{timestamp}.json"
    filepath = os.path.join(settings.BACKUP_DIR, filename)

    # Local backup
    subprocess.call([
        "python", "manage.py", "dumpdata",
        "--natural-primary", "--natural-foreign",
        "--indent", "2", "-o", filepath
    ])

    # Encrypt (optional)
    encrypt_file(filepath)

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    # Upload
    try:
        s3.upload_file(filepath, settings.AWS_STORAGE_BUCKET_NAME, f"backups/{filename}")
        upload_status = "Uploaded to S3"
    except Exception as e:
        upload_status = f"Cloud upload failed: {e}"

    # Cleanup (older than 7 days)
    try:
        response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix="backups/")
        if "Contents" in response:
            for obj in response["Contents"]:
                last_modified = obj["LastModified"].replace(tzinfo=None)
                if (datetime.datetime.now() - last_modified).days > 7:
                    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=obj["Key"])
                    print(f"🗑️ Deleted old backup: {obj['Key']}")
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

    BackupLog.objects.create(filename=filename, status=upload_status, is_auto=auto)


# --- Make this top-level so it can be serialized ---
def scheduled_backup_job():
    backup_and_cleanup(auto=True)


def start_scheduler():
    """Start background scheduler once Django starts."""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Add job via full path (text reference)
    from cores.tasks import scheduled_backup_job

    scheduler.add_job(
    scheduled_backup_job,      
    trigger='cron',
    hour=2,
    minute=0,
    id='daily_backup_job',
    replace_existing=True,
)



    register_events(scheduler)
    scheduler.start()
    print("🕒 Daily backup scheduler running.")
