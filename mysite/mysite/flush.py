# 이미 생긴 연동 세션 초기화
def logout_view(request):
    request.session.flush()  # 세션 초기화
