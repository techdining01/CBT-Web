import os
import subprocess
import datetime
import boto3
from django.conf import settings
from django.http import FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage


# ---------- MANUAL BACKUP ----------
@staff_member_required
def backup_database(request):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    filename = f"cbt_backup_{timestamp}.json"
    filepath = os.path.join(settings.BACKUP_DIR, filename)

    # Dump DB to JSON
    subprocess.call([
        "python", "manage.py", "dumpdata",
        "--natural-primary", "--natural-foreign",
        "--indent", "2", "-o", filepath
    ])

    # Upload to S3
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3.upload_file(filepath, settings.AWS_STORAGE_BUCKET_NAME, f"backups/{filename}")
        upload_msg = "✅ Uploaded to S3 successfully."
    except Exception as e:
        upload_msg = f"⚠️ Cloud upload failed: {e}"

    return FileResponse(open(filepath, "rb"), as_attachment=True, filename=filename)


# ---------- RESTORE BACKUP ----------@staff_member_required
def restore_database(request):
    if request.method == "POST" and request.FILES.get("backup_file"):
        file = request.FILES["backup_file"]
        file_path = default_storage.save("tmp/restore.json", file)

        # Load backup
        subprocess.call(["python", "manage.py", "loaddata", file_path])

        return redirect("admin_dashboard")

    return render(request, "exams/restore_database.html")


# ---------- SESSION TIMEOUT ---------- #

def session_expired(request):
    return render(request, 'exams/session_expired.html')

