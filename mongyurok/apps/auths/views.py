from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate, get_user_model
from django.contrib.auth import get_user_model
import random
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import EmailVerification
from django.db.models import F
from django.shortcuts import render, redirect
from django.contrib.auth import logout

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:

            auth_login(request, user)
            return redirect('characters:main')
        else:

            return render(request, 'auths/login.html', {
                'error': '이메일 또는 비밀번호가 틀렸습니다.'
            })

    return render(request, 'auths/login.html')

def sign_view(request):
    return render(request, 'auths/sign.html')

def sign_form_view(request):
    return render(request, 'auths/sign_form.html')

def sign_up(request):
    if request.method == 'POST':
        email_id = request.POST.get('email_id')
        domain = request.POST.get('email_domain')
        password = request.POST.get('password')
        nickname = request.POST.get('nickname')

        profile_img = request.FILES.get('profile_image')

        full_email = f"{email_id}@{domain}"
        try:
            if User.objects.filter(email=full_email).exists():
                return JsonResponse({'status': 'error', 'message': '이미 가입된 이메일입니다'})
            user = User.objects.create_user(
                email=full_email,
                password=password,
                nickname=nickname,
                state=1,           # 기본 상태값 (예: 활성 유저)
                login_failed=0     # 초기 실패 횟수
            )

            if profile_img:
                    user.img_url = profile_img  # 장고가 알아서 파일 저장 및 경로 기록
                    user.save()
            return JsonResponse({'status': 'success', 'message': '회원가입에 성공하였습니다'})
        except Exception as e:
            print(f"회원가입 에러: {e}")
            return JsonResponse({'status': 'error', 'message': f'서버 오류: {str(e)}'})

def password_find(request):
    return render(request, "auths/find.html")

def password_reset(request):
    return render(request, "auths/password_reset.html")

def privacy(request):
    return render(request, "auths/privacy.html")

def terms(request):
    return render(request, "auths/terms.html")

def send_verification_code(request):
    # 1. POST 요청이 아니면 바로 차단
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '잘못된 접근입니다.'})

    try:
        email_id = request.POST.get('email_id')
        domain = request.POST.get('email_domain')
        full_email = f"{email_id}@{domain}"
        code = str(random.randint(100000, 999999))

        # DB 처리
        verification, created = EmailVerification.objects.get_or_create(
            email=full_email,
            defaults={'code': code, 'send_count': 1}
        )

        if not created:
            # 횟수 제한 체크를 전송 전에 수행
            if verification.send_count >= 5:
                return JsonResponse({
                    'status': 'error', 
                    'message': '일일 전송 제한 24시간 후 다시 시도해 주세요'
                })
            
            verification.code = code
            verification.is_verified = False 
            verification.send_count += 1 
            verification.save()

        # 2. 이메일 전송 로직
        subject = "인증번호 안내"
        from_email = "jiji0313233@gmail.com"
        to_email = [full_email]
        html_content = f"""
            <div style="font-family: Arial; padding: 20px; text-align: center;">
                <h1 style="color:#333;">🗝️몽유록 인증번호 안내🗝️</h1>
                <div style="margin: 30px auto; padding: 20px; width: 200px; font-size: 28px; font-weight: bold; color: #ffffff; background: #315057; border-radius: 10px; letter-spacing: 5px;">
                    {code}
                </div>
                <p style="color:#777;">해당 인증번호를 입력해주세요.</p>
            </div>
        """

        msg = EmailMultiAlternatives(subject, "", from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # 성공 리턴 (반드시 여기서 확실하게 종료)
        return JsonResponse({'status': 'success', 'message': '인증번호가 전송되었습니다'})

    except Exception as e:
        # 에러 발생 시 로그를 찍고 에러 응답
        print(f"Error: {e}")
        return JsonResponse({'status': 'error', 'message': '서버 오류가 발생했습니다.'}, status=500)

def code_confirm(request):
    if request.method == 'POST':
        email_id = request.POST.get('email_id')
        code = request.POST.get('code')
        domain = request.POST.get('email_domain')
        full_email = f"{email_id}@{domain}"
        print(full_email)

        try:
            verification = EmailVerification.objects.get(email=full_email)

            if verification.code == code:
                verification.is_verified = True
                verification.save()
                return JsonResponse({'status': 'success', 'message': '이메일 인증에 성공하였습니다'})
            else:
                return JsonResponse({'status': 'error', 'message': '이메일 인증 번호가 맞지 않습니다.'})

        except EmailVerification.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '인증 요청 기록이 없습니다.'})

def logout_view(request):
    logout(request)
    return redirect('auths:login')
