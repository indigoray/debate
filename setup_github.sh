#!/bin/bash

echo "🚀 GitHub 저장소 연결 스크립트"
echo "================================"

# GitHub 사용자명 입력
read -p "GitHub 사용자명을 입력하세요: " github_username

if [ -z "$github_username" ]; then
    echo "❌ 사용자명이 입력되지 않았습니다."
    exit 1
fi

echo "📝 GitHub 사용자명: $github_username"

# 원격 저장소 URL 설정
remote_url="https://github.com/$github_username/debate.git"

echo "🔗 원격 저장소 연결 중..."
git remote add origin $remote_url

if [ $? -eq 0 ]; then
    echo "✅ 원격 저장소 연결 성공"
else
    echo "❌ 원격 저장소 연결 실패"
    exit 1
fi

echo "🔄 브랜치를 main으로 변경 중..."
git branch -M main

echo "📤 GitHub에 코드 푸시 중..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "🎉 성공적으로 GitHub에 업로드되었습니다!"
    echo "📖 저장소 URL: https://github.com/$github_username/debate"
else
    echo "❌ 푸시 실패. GitHub 저장소가 생성되었는지 확인하세요."
    echo "💡 GitHub에서 'debate' 저장소를 먼저 생성해주세요."
fi 