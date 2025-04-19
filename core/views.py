from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import User, VideoUpload, MIDetection, Diagnosis, RoleChangeHistory  # Your custom user model
from django.contrib import messages
import requests


def home(request):
    return render(request, 'core/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Incorrect username or password')
    return render(request, 'core/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            user = User.objects.create_user(username=username, password=password, role=role)
            messages.success(request, 'Registration successful')
            return redirect('login')
    return render(request, 'core/register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return HttpResponseForbidden("Permission denied")

    videos = VideoUpload.objects.filter(patient=request.user).order_by('-upload_time')
    return render(request, 'core/patient_dashboard.html', {'videos': videos})


@login_required
def download_video(request, video_id):
    video = get_object_or_404(VideoUpload, id=video_id, patient=request.user)
    response = FileResponse(video.video.open('rb'), as_attachment=True,
                            filename=video.video.name.split('/')[-1])
    return response


@login_required
def download_diagnosis(request, video_id):
    video = get_object_or_404(VideoUpload, id=video_id, patient=request.user)
    diagnoses = Diagnosis.objects.filter(video=video).order_by('created_at')

    if not diagnoses.exists():
        return HttpResponse("No diagnosis records available", content_type='text/plain')

    content = f"Video upload time: {video.upload_time}\n"
    content += f"Patient: {video.patient.username}\n\n"
    content += "【Diagnosis Records】\n"
    for d in diagnoses:
        content += f"- {d.created_at.strftime('%Y-%m-%d %H:%M:%S')} Doctor {d.doctor.username}: {d.diagnosis_text}\n"

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename=diagnosis_video_{video.id}.txt'
    return response


@login_required
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        if request.user.role != 'patient':
            messages.error(request, "Only patients can upload videos")
            return redirect('video_list')

        video_file = request.FILES['video']
        VideoUpload.objects.create(patient=request.user, video=video_file)
        messages.success(request, "Video uploaded successfully")
        return redirect('video_list')

    return render(request, 'core/upload_video.html')


@login_required
def video_list(request):
    videos = VideoUpload.objects.filter(patient=request.user)
    return render(request, 'core/video_list.html', {'videos': videos})


def classify_view(request, video_id):
    video = VideoUpload.objects.get(id=video_id)
    video_path = video.video.path

    # Simulate sending to model API (use your own model API address)
    response = requests.post('http://localhost:8001/classify', files={'file': open(video_path, 'rb')})
    result = response.json()

    classification = result.get('classification', 'Unknown')

    # Save classification result
    video.classification_result = classification
    video.save()

    # Return JSON to the frontend (frontend decides whether to show a popup)
    return JsonResponse({'classification': classification})


def detect_mi_view(request, video_id):
    video = get_object_or_404(VideoUpload, id=video_id)
    user = request.user
    video_path = video.video_file.path

    # Simulated model API URLs
    model1_api = 'http://127.0.0.1:8002/model1_mi'
    model2_api = 'http://127.0.0.1:8003/model2_mi'

    try:
        with open(video_path, 'rb') as f:
            files = {'file': f}

            # Call model1
            res1 = requests.post(model1_api, files=files).json()
            result1 = res1.get('result', 'Unknown')

        with open(video_path, 'rb') as f:
            files = {'file': f}

            # Call model2
            res2 = requests.post(model2_api, files=files).json()
            result2 = res2.get('result', 'Unknown')

        # Combined judgment: if any result is MI, the final result is MI
        final = 'MI' if 'MI' in [result1, result2] else 'Normal'

        # Save detection record
        MIDetection.objects.create(
            patient=user,
            video=video,
            result_model1=result1,
            result_model2=result2,
            final_result=final
        )

        return JsonResponse({
            'model1_result': result1,
            'model2_result': result2,
            'final_result': final
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return HttpResponseForbidden("Permission denied")

    videos = VideoUpload.objects.all().order_by('-upload_time')
    return render(request, 'core/doctor_dashboard.html', {'videos': videos})


@login_required
def diagnose_video(request, video_id):
    if request.user.role != 'doctor':
        return HttpResponseForbidden("Permission denied")

    video = get_object_or_404(VideoUpload, id=video_id)
    patient = video.patient
    previous_diagnoses = Diagnosis.objects.filter(video=video).order_by('-created_at')
    last_diagnosis = previous_diagnoses.first()

    if request.method == 'POST':
        text = request.POST.get('diagnosis_text', '').strip()
        if text:
            Diagnosis.objects.create(
                doctor=request.user,
                patient=patient,
                video=video,
                diagnosis_text=text
            )
            messages.success(request, "Diagnosis saved")
            return redirect('diagnose_video', video_id=video.id)
        else:
            messages.error(request, "Diagnosis text cannot be empty")

    return render(request, 'core/diagnose_video.html', {
        'video': video,
        'patient': patient,
        'previous_diagnoses': previous_diagnoses,
        'last_diagnosis': last_diagnosis,
    })


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Permission denied")

    users = User.objects.all()
    return render(request, 'core/admin_dashboard.html', {'users': users})


@login_required
def change_user_role(request, user_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Permission denied")

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_role = request.POST['role']
        old_role = user.role

        if old_role != new_role:
            RoleChangeHistory.objects.create(
                admin=request.user,
                user=user,
                old_role=old_role,
                new_role=new_role
            )
            user.role = new_role
            user.save()
            messages.success(request, f"User {user.username}'s role has been updated to {new_role}")
        else:
            messages.warning(request, "New role is the same as the old role")

        return redirect('admin_manage_dashboard')


@login_required
def role_change_history(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Permission denied")

    role_changes = RoleChangeHistory.objects.select_related('admin', 'user').order_by('-change_date')
    return render(request, 'core/role_change_history.html', {'role_changes': role_changes})


@login_required
def admin_all_users_view(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Permission denied")

    users = User.objects.all()
    return render(request, 'core/admin_all_users.html', {'users': users})


@login_required
def edit_user_info(request, user_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Permission denied")

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')

        if username and email and role:
            # Update user information
            user.username = username
            user.email = email
            old_role = user.role
            if old_role != role:
                # Save role change record
                RoleChangeHistory.objects.create(
                    admin=request.user,
                    user=user,
                    old_role=old_role,
                    new_role=role
                )
            user.role = role
            user.save()
            messages.success(request, f'User {user.username} info updated')
            return redirect('admin_all_users')
        else:
            messages.error(request, 'All fields are required')

    return render(request, 'core/edit_user_info.html', {'user': user})


@login_required
def admin_video_records(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Permission denied")

    videos = VideoUpload.objects.select_related('patient').order_by('-upload_time')
    return render(request, 'core/admin_video_records.html', {'videos': videos})
