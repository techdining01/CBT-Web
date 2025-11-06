from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Notification
from django.urls import reverse
from .forms import TeacherAdminForm, EditUserRegistrationForm, EditTeacherAdminForm, UserRegistrationForm, loginForm
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST   
from exams.models import ActionLog  

User = get_user_model()


def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user_id = user.id
            role = user.role
            if role in ['admin', 'teacher']:
                messages.success(request, f'{user.role.title()} account created successfully. Awaiting approval.')
                url = reverse('teacheradminprofile', kwargs={'user_id': user_id})
                return redirect(url)
            else:
                messages.success(request, "Registration successful. Please wait for approval.")
            return redirect("dashboard")
    else:
        form = UserRegistrationForm()
    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = loginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user.approved == True:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name} 👋")
                return redirect('dashboard')
            else:
                messages.info(request, 'Ensure you have been approval by Admin')
        messages.error(request, "Invalid username or password.")
    else:
        form = loginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')



def teacheradminprofile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = TeacherAdminForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            if request.user.is_authenticated:
                messages.success(request, f'{user.role.title()} profile updated successfully. wait for approval')
                return redirect('dashboard')
            messages.success(request, f'{user.role.title()} profile created successfully. wait for approval')
            return redirect('login')
    else:
        form = TeacherAdminForm()


    context = {'form': form, 'user': user}

    return render(request, "users/teacheradminprofile.html", context )


@login_required
def view_profile(request):
    """Read-only profile page for Student, Teacher, Admin."""
    return render(request, "users/view_profile.html", {"user": request.user})



@login_required
def edit_user(request, user_id):
    """Allow Student, Teacher, or Admin to update their profile."""

    user = get_object_or_404(User, id=user_id)

    # Pick form by role
    form_class = EditUserRegistrationForm if user.role == "student" else EditTeacherAdminForm

    if request.method == "POST":
        old_data = {
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
        form = form_class(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_user = form.save()
            new_data = {
                "username": updated_user.username,
                "email": updated_user.email,
                "role": updated_user.role,
            }
            # Log the edit
            ActionLog.objects.create(
                user=request.user,
                action_type="Edit User",
                model_name="User",
                object_id=str(updated_user.id),
                details={"old": old_data, "new": new_data, "target": updated_user.username},
            )
            messages.success(request, "Profile updated successfully!")

                # Redirect back to dashboard
            if request.user.is_authenticated == "student":
                return redirect("student_dashboard")
            elif request.user.is_authenticated == "teacher":
                return redirect("teacher_dashboard")
            else:
                return redirect("admin_dashboard")
    else:
        form = form_class(instance=user)


    return render(request, "users/edit_profile.html", {"form": form, "user": user})

            

def create_user(request):
    return redirect('signup')



def is_admin_or_superadmin(user):
    return user.role in ["admin", "superadmin"]


@login_required
@user_passes_test(is_admin_or_superadmin)
def user_approval_list(request):
    users = User.objects.exclude(role="superadmin")  # Exclude superadmins
    return render(request, "users/user_approval_list.html", {"users": users})


@login_required
@user_passes_test(is_admin_or_superadmin)
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.approved = True
    user.save()
    messages.success(request, f"{user.username} has been approved ✅.")
    return redirect("user_approval_list")


@login_required
@user_passes_test(is_admin_or_superadmin)
def reject_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.approved = False
    user.delete()
    messages.warning(request, f"{user.username} has been rejected ❌.")
    return redirect("user_approval_list")


@login_required
@user_passes_test(is_admin_or_superadmin)
def pending_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.approved = False
    user.save()
    messages.info(request, f"{user.username} is now pending ⏳.")
    return redirect("user_approval_list")



def is_admin(user):
    return user.is_authenticated and (user.role in ['superadmin', 'admin'])


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """
    Renders main Manage Users page with AJAX support.
    """
    return render(request, "users/manage_users.html")


@login_required
@user_passes_test(is_admin)
def load_users(request):
    """
    Handles AJAX pagination and search
    """
    search = request.GET.get("search", "")
    page = request.GET.get("page", 1)

    users = User.objects.exclude(role="superadmin").order_by("-date_joined")

    if search:
        users = users.filter(username__icontains=search) | users.filter(first_name__icontains=search) | users.filter(last_name__icontains=search) | users.filter(email__icontains=search)

    page = Paginator(users, 10)  
    users_page = page.get_page(request.GET.get('page'))

    data = {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'student_class': str(u.student_class),
                "email": u.email,
                "role": u.role,
                "date_joined": u.date_joined.strftime("%d-%m-%Y %H:%M"),
            }
            for u in users_page
        ],
        "has_next": users_page.has_next(),
        "has_previous": users_page.has_previous(),
        "num_pages": page.num_pages,
        "current_page": users_page.number,
    }
    print(data)
    return JsonResponse(data)


@require_POST
def update_user(request, user_id):
    """Edit user details via AJAX"""
    user = get_object_or_404(User, id=user_id)

    old_data = {
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }

    username = request.POST.get("username")
    email = request.POST.get("email")
    role = request.POST.get("role")

    if username:
        user.username = username
    if email:
        user.email = email
    if role in dict(User.ROLE_CHOICES):
        user.role = role

    user.save()

    # Log action
    ActionLog.objects.create(
        user=request.user,
        action_type="Edited user",
        model_name="User",
        object_id=user.id,
        details={
            "old": old_data,
            "new": {"username": user.username, "email": user.email, "role": user.role},
        },
    )

    return JsonResponse({
        "success": True,
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.get_role_display(),
    })


@require_POST
def delete_user(request, user_id):
    """Delete user via AJAX"""
    user = get_object_or_404(User, id=user_id)
    if user.role == "superadmin":
        return JsonResponse({"success": False, "message": "Cannot delete superadmin"})
    
    user_data = {"username": user.username, "email": user.email, "role": user.role}

    user.delete()

    # Log action
    ActionLog.objects.create(
        user=request.user,
        action_type="Deleted user",
        model_name="User",
        object_id=user_id,
        details=user_data,
    )

    return JsonResponse({"success": True, "id": user_id})


@login_required
def dashboard_redirect(request):
    if request.user.role == "superadmin":
        return redirect("superadmin_dashboard")
    elif request.user.role == "admin":
        return redirect("admin_dashboard")
    elif request.user.role == "teacher":
        return redirect("teacher_dashboard")
    elif request.user.role == "student":
        return redirect("student_dashboard")
    else:
        messages.error(request, "Unknown role. Contact SuperAdmin.")
        return redirect("login")


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    messages.success(request, "Notification marked as read ✅")
    return redirect("dashboard")


@login_required
def send_broadcast(request):
    if request.method == "POST":
        message = request.POST.get("message")
        sender = request.user

        # Decide recipients
        if sender.role == "admin":
            recipients = User.objects.filter(role__in=["teacher", "student"])
        elif sender.role == "teacher":
            recipients = User.objects.filter(role="student")
        else:
            messages.error(request, "You cannot send broadcasts.")
            return redirect("dashboard")

        # Create notifications
        for recipient in recipients:
            Notification.objects.create(
                sender=sender,
                recipient=recipient,
                message=message,
                role=recipient.role,
            )

        messages.success(request, "Broadcast sent successfully ✅")
    return redirect("dashboard")


from .models import User, UserStatusLog

def update_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    new_status = request.POST.get("status")  # "approve" / "reject" / "pending"

    if new_status not in ["approve", "reject", "pending"]:
        messages.error(request, "Invalid status")
        return redirect("manage_users")

    old_status = user.status  # assuming User model has a `status` field
    user.status = new_status
    user.save()

    # Log change
    UserStatusLog.objects.create(
        user=user,
        old_status=old_status,
        new_status=new_status,
        changed_by=request.user,
        changed_at=timezone.now()
    )

    messages.success(request, f"{user.username}'s status updated to {new_status}.")
    return redirect("manage_users")
