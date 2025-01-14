# NewsSummarizer

# 뉴스 요약기 (News Summarizer)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-brightgreen.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-latest-orange.svg)

뉴스 기사를 자동으로 요약해주는 데스크톱 애플리케이션입니다. PyQt5로 제작된 직관적인 GUI를 통해 손쉽게 뉴스 기사를 요약하고 인사이트를 얻을 수 있습니다.

## 주요 기능

- 🔗 URL을 통한 뉴스 기사 내용 자동 추출
- 📋 클립보드에서 URL 빠른 불러오기
- 📝 OpenAI API를 활용한 기사 요약
- 🎯 요약본 맞춤 수정 기능
- 💡 기사에 대한 추가 인사이트 제공
- 🔒 API 키 로컬 저장 기능

## 설치 방법

1. 저장소 클론
    ```bash
    git clone https://github.com/yourusername/news-summarizer.git
    cd news-summarizer
    ```

2. 필요한 패키지 설치
    ```bash
    pip install -r requirements.txt
    ```

3. 애플리케이션 실행
    ```bash
    python main.py
    ```

## 필요 사항

- Python 3.7 이상
- OpenAI API 키
- 인터넷 연결

## 의존성 패키지

- PyQt5
- requests
- beautifulsoup4
- pyperclip
- openai

## 사용 방법

1. OpenAI API 키를 입력합니다.
2. 요약하고 싶은 뉴스 기사의 URL을 입력하거나 클립보드에서 가져옵니다.
3. "요약하기" 버튼을 클릭하여 기사를 요약합니다.
4. 필요한 경우 추가 의견을 입력하여 요약을 다듬을 수 있습니다.
5. "인사이트" 탭에서 기사에 대한 추가 분석을 확인할 수 있습니다.

## 스크린샷

![NS_v1](./screenshot.png)

## 🧑‍💻 개발자

- **GitHub**: [@GMR-archive](https://github.com/GMR-archive)
- **BLOG**: [G엠알의 게이밍아카이브](https://blog.naver.com/gmr_archive)
