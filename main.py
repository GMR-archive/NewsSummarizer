import sys
import os
import logging
import threading
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QTextEdit, QPushButton, QTabWidget, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from bs4 import BeautifulSoup
import pyperclip

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

class NewsSummarizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("뉴스 요약기")
        self.resize(800, 700)

        # 설정 파일 경로
        self.config_path = os.path.expanduser('~/.news_summarizer_config')

        # UI 초기화
        self.init_ui()

        # 설정 로드
        self.load_config()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.summary_tab = QWidget()
        self.insights_tab = QWidget()

        self.tabs.addTab(self.summary_tab, "요약")
        self.tabs.addTab(self.insights_tab, "인사이트")

        self.init_summary_tab()
        self.init_insights_tab()

    def init_summary_tab(self):
        layout = QVBoxLayout()

        # API 키 입력
        api_layout = QHBoxLayout()
        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_key_label)
        api_layout.addWidget(self.api_key_input)
        layout.addLayout(api_layout)

        # URL 입력
        url_layout = QHBoxLayout()
        self.url_label = QLabel("뉴스 기사 URL:")
        self.url_input = QLineEdit()
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        self.clipboard_button = QPushButton("클립보드에서 URL 가져오기")
        self.summarize_button = QPushButton("요약하기")
        self.clipboard_button.clicked.connect(self.get_url_from_clipboard)
        self.summarize_button.clicked.connect(self.start_summarize_thread)
        button_layout.addWidget(self.clipboard_button)
        button_layout.addWidget(self.summarize_button)
        layout.addLayout(button_layout)

        # 요약 출력
        self.summary_output = QTextEdit()
        self.summary_output.setReadOnly(True)
        layout.addWidget(self.summary_output)

        # 추가 의견 입력
        refine_layout = QHBoxLayout()
        self.refinement_label = QLabel("추가 의견:")
        self.refinement_input = QLineEdit()
        self.refine_button = QPushButton("요약 다듬기")
        self.refine_button.clicked.connect(self.start_refine_thread)
        refine_layout.addWidget(self.refinement_label)
        refine_layout.addWidget(self.refinement_input)
        refine_layout.addWidget(self.refine_button)
        layout.addLayout(refine_layout)

        self.summary_tab.setLayout(layout)

    def init_insights_tab(self):
        layout = QVBoxLayout()
        self.insights_output = QTextEdit()
        self.insights_output.setReadOnly(True)
        layout.addWidget(self.insights_output)
        self.insights_tab.setLayout(layout)

    def get_url_from_clipboard(self):
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content and clipboard_content.startswith(('http://', 'https://')):
                self.url_input.setText(clipboard_content)
            else:
                QMessageBox.information(self, "알림", "클립보드에 유효한 URL이 없습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"클립보드 접근 중 오류: {e}")

    def start_summarize_thread(self):
        threading.Thread(target=self.summarize_article, daemon=True).start()

    def start_refine_thread(self):
        threading.Thread(target=self.refine_summary, daemon=True).start()

    def extract_article_content(self, url):
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')

            article_texts = []
            selectors = ['article', 'div.article-content', 'div.content', 'div[class*="article"]', 'div[class*="content"]', 'p']
            
            for selector in selectors:
                for elem in soup.select(selector):
                    text = elem.get_text(strip=True)
                    if len(text) > 50:
                        article_texts.append(text)

            article_text = ' '.join(dict.fromkeys(article_texts))
            logging.info(f"추출된 기사 길이: {len(article_text)} 자")
            return article_text[:10000]
        except Exception as e:
            logging.error(f"기사 추출 오류: {e}")
            QMessageBox.critical(self, "오류", f"기사 추출 중 오류: {e}")
            return ""

    def summarize_article(self):
        api_key = self.api_key_input.text()
        url = self.url_input.text()

        if not api_key or not url:
            QMessageBox.critical(self, "오류", "API 키와 URL을 입력해주세요")
            return

        article_content = self.extract_article_content(url)
        if not article_content:
            return

        # OpenAI API 호출은 예시로 남겨둡니다.
        self.summary_output.setPlainText("요약 결과를 여기에 표시합니다 (테스트 데이터)")

    def refine_summary(self):
        api_key = self.api_key_input.text()
        refinement = self.refinement_input.text()
        current_summary = self.summary_output.toPlainText()

        if not api_key or not refinement:
            QMessageBox.critical(self, "오류", "API 키와 개선 의견을 입력해주세요")
            return

        # OpenAI API 호출은 예시로 남겨둡니다.
        self.summary_output.setPlainText("다듬어진 요약 결과를 여기에 표시합니다 (테스트 데이터)")

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = f.read().strip()
                    self.api_key_input.setText(config)
        except Exception as e:
            logging.error(f"설정 로드 중 오류: {e}")

    def closeEvent(self, event):
        try:
            with open(self.config_path, 'w') as f:
                f.write(self.api_key_input.text())
        except Exception as e:
            logging.error(f"설정 저장 중 오류: {e}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewsSummarizerApp()
    window.show()
    sys.exit(app.exec_())
