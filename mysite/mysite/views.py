import json

import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings

# GitHub OAuth 인증 URL로 리디렉션
def github_oauth(request):
    github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope=repo,read:org,admin:repo_hook"
    return redirect(github_oauth_url)

# GitHub OAuth 인증 콜백
def github_oauth_callback(request):
    code = request.GET.get('code')

    # GitHub 액세스 토큰 요청
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.GITHUB_REDIRECT_URI
    }

    response = requests.post(token_url, data=payload, headers={'Accept': 'application/json'})
    response_data = response.json()

    # 액세스 토큰을 세션에 저장
    access_token = response_data.get('access_token')

    if access_token:
        request.session['github_access_token'] = access_token

        # 사용자의 GitHub 사용자명 정보 가져오기
        user_info_url = "https://api.github.com/user"
        headers = {'Authorization': f'token {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info = user_info_response.json()

        # 사용자명 저장
        github_username = user_info.get('login')
        request.session['github_username'] = github_username

        return redirect('org_list')  # 인증 후 조직 목록 페이지로 리디렉션
    else:
        return JsonResponse({"message": "OAuth 인증 실패"})

# 사용자 조직 목록을 가져오는 함수
def get_user_orgs(request):
    access_token = request.session.get('github_access_token')

    if access_token:
        headers = {
            'Authorization': f'token {access_token}'
        }
        response = requests.get('https://api.github.com/user/orgs', headers=headers)
        orgs = response.json()
        return orgs
    else:
        return []

# 조직 목록 페이지
def org_list(request):
    organizations = get_user_orgs(request)
    return render(request, 'mysite/org_list.html', {'organizations': organizations})

# 특정 조직의 리포지토리 목록을 가져오는 함수
def get_org_repos(request, org_name):
    access_token = request.session.get('github_access_token')

    if access_token:
        headers = {
            'Authorization': f'token {access_token}'
        }
        response = requests.get(f'https://api.github.com/orgs/{org_name}/repos', headers=headers)
        repos = response.json()
        return repos
    else:
        return []

# 특정 조직의 리포지토리 목록 페이지
def org_repos(request, org_name):
    repositories = get_org_repos(request, org_name)
    return render(request, 'mysite/repo_list.html', {'repositories': repositories, 'org_name': org_name})

# 리포지토리에 웹훅을 설정하는 함수
def create_webhook(org_name, repo_name, access_token, github_username):
    #url = f'https://api.github.com/repos/{github_username}/{repo_name}/hooks'  # 사용자명 동적으로 사용
    repo_path = f"{org_name}/{repo_name}"

    # 요청할 URL
    url = f'https://api.github.com/repos/{repo_path}/hooks'
    # 디버깅 로그: 리포지토리 경로와 요청 URL
    print(f"Repository Path: {repo_path}")
    print(f"Requesting URL: {url}")
    headers = {
        'Authorization': f'token {access_token}',
        'Content-Type': 'application/json'
    }

    # 웹훅 설정 데이터 (로컬 테스트용 URL)
    payload = {
        "name": "web",
        "active": True,
        "events": ["pull_request"],  # PR 관련 이벤트만 받음
        "config": {
            "url": f"{settings.GITHUB_WEBHOOK_URL}",  # 로컬 웹훅 수신 URL
            "content_type": "json"
        }
    }

    # 디버깅 로그: 요청 본문
    print(f"Request Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(url, json=payload, headers=headers)

    # 디버깅 로그: 응답 상태 코드와 응답 본문
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    # 응답이 성공적이라면
    if response.status_code == 201:
        print(f"Webhook created successfully for {github_username}/{repo_name}")
        return True
    else:
        # 응답이 실패하면 상태 코드와 메시지 출력
        print(f"Failed to create webhook for {github_username}/{repo_name}")
        print(f"Error Details: {response.json() if response.status_code != 404 else response.text}")
        return False

# 웹훅 설정을 처리하는 함수
def setup_webhook(request, org_name, repo_name):
    access_token = request.session.get('github_access_token')
    github_username = request.session.get('github_username')  # 세션에서 사용자명 가져오기
    if access_token and github_username:
        # 웹훅 설정
        success = create_webhook(org_name, repo_name, access_token, github_username)
        if success:
            return JsonResponse({"message": f"Webhook for {repo_name} created successfully!"})
        else:
            return JsonResponse({"message": "Failed to create webhook."}, status=400)
    else:
        return JsonResponse({"message": "Access token or GitHub username not found."}, status=400)

# GitHub에서 PR 이벤트를 수신하는 웹훅 엔드포인트
def github_webhook(request):
    # GitHub에서 전달하는 PR 이벤트 정보 확인
    if request.method == "POST":
        data = request.json()

        # PR 이벤트인지 확인
        if data.get('action') == 'opened' and data.get('pull_request'):
            pr_number = data['pull_request']['number']
            pr_url = data['pull_request']['html_url']
            pr_title = data['pull_request']['title']

            # PR에 댓글 달기
            access_token = request.session.get('github_access_token')
            github_username = request.session.get('github_username')  # 세션에서 사용자명 가져오기
            if access_token and github_username:
                headers = {
                    'Authorization': f'token {access_token}',
                    'Content-Type': 'application/json'
                }
                comment_payload = {
                    'body': f'PR {pr_number} titled "{pr_title}" has been detected!'
                }

                # PR에 댓글을 달기 위한 API 호출
                comment_url = f"https://api.github.com/repos/{github_username}/{data['repository']['name']}/issues/{pr_number}/comments"
                requests.post(comment_url, json=comment_payload, headers=headers)

        return JsonResponse({"message": "Webhook received and processed."})
    else:
        return JsonResponse({"message": "Invalid request method."}, status=405)
