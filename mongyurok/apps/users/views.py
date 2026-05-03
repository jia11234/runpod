from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse
import re

@login_required
def mypage(request):
    user = request.user
    User = get_user_model()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "nickname":
            nickname = request.POST.get("nickname", "").strip()

            if not nickname:
                return redirect("users:mypage")

            if not re.match(r"^[가-힣a-zA-Z0-9]{2,12}$", nickname):
                return render(request, "users/mypage.html", {
                    "nickname_error": "올바른 닉네임 형식이 아닙니다. 다시 입력해 주세요."
                })

            if nickname == user.nickname:
                return render(request, "users/mypage.html", {
                    "nickname_error": "기존 닉네임과 동일합니다. 다시 입력해 주세요."
                })

            if User.objects.filter(nickname=nickname).exclude(pk=user.pk).exists():
                return render(request, "users/mypage.html", {
                    "nickname_error": "이미 사용 중인 닉네임입니다."
                })

            user.nickname = nickname
            user.save()

            messages.success(request, "닉네임 수정을 완료했어요")
            return redirect("users:mypage")

        if action == "profile_image":
            profile_image = request.FILES.get("profile_image")

            if not profile_image:
                messages.error(request, "프로필 수정을 실패했어요")
                return redirect("users:mypage")

            allowed_types = ["image/jpeg", "image/png"]

            if profile_image.content_type not in allowed_types:
                messages.error(request, "프로필 수정을 실패했어요")
                return redirect("users:mypage")

            if profile_image.size > 5 * 1024 * 1024:
                messages.error(request, "프로필 수정을 실패했어요")
                return redirect("users:mypage")

            user.img_url = profile_image
            user.save()

            messages.success(request, "프로필 수정을 완료했어요")
            return redirect("users:mypage")

    return render(request, "users/mypage.html")


@login_required
def pwd_change(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password", "").strip()
        new_password = request.POST.get("new_password", "").strip()
        new_password_confirm = request.POST.get("new_password_confirm", "").strip()

        user = request.user

        password_regex = r"^(?=.*[A-Za-z])(?=.*\d.*\d)(?=.*[!@#$%^&*?~])[A-Za-z\d!@#$%^&*?~]{8,16}$"

        current_password_error = ""
        new_password_error = ""
        confirm_password_error = ""

        if not current_password or not user.check_password(current_password):
            current_password_error = "비밀번호가 일치하지 않습니다."

        if not re.match(password_regex, new_password):
            new_password_error = "비밀번호 형식이 올바르지 않습니다."

        if new_password != new_password_confirm:
            confirm_password_error = "비밀번호가 일치하지 않습니다."

        if current_password_error or new_password_error or confirm_password_error:
            messages.error(request, "비밀번호 변경에 실패했습니다. 다시 시도해 주세요.")
            return render(request, "users/pwd_change.html", {
                "current_password_error": current_password_error,
                "new_password_error": new_password_error,
                "confirm_password_error": confirm_password_error,
            })

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)

        messages.success(request, "비밀번호 수정이 완료되었습니다.")
        return redirect("users:mypage")

    return render(request, "users/pwd_change.html")



@login_required
def delete_account(request):
    if request.method == "POST":
        password = request.POST.get("password", "")
        user = request.user

        if not password or not user.check_password(password):
            return render(request, "users/delete_account.html", {
                "password_error": "비밀번호가 일치하지 않습니다."
            })

        user.delete()
        logout(request)

        return HttpResponse("""
            <script>
                alert("회원탈퇴가 완료되었습니다.");
                location.href = "/";
            </script>
        """)

    return render(request, "users/delete_account.html")