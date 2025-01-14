import sys
import os
import logging
import threading
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QTextEdit, QPushButton, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from bs4 import BeautifulSoup
import pyperclip
from openai import OpenAI

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# 스레드 안전한 시그널을 위한 클래스
class WorkerSignals(QObject):
    update_summary = pyqtSignal(str, str)
    update_refined = pyqtSignal(str)
    error = pyqtSignal(str)

class NewsSummarizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("뉴스 요약기")
        self.resize(800, 700)
        
        # 시그널 객체 초기화
        self.signals = WorkerSignals()
        self.signals.update_summary.connect(self._update_summary_ui)
        self.signals.update_refined.connect(self._update_refined_summary)
        self.signals.error.connect(self._show_error)

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
            selectors = [
                'article', 
                'div.article-content', 
                'div.content', 
                'div[class*="article"]', 
                'div[class*="content"]', 
                'p'
            ]
            
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
            self.signals.error.emit(f"기사 추출 중 오류: {e}")
            return ""

    def summarize_article(self):
        try:
            api_key = self.api_key_input.text()
            url = self.url_input.text()
            
            if not api_key or not url:
                self.signals.error.emit("API 키와 URL을 입력해주세요")
                return
            
            article_content = self.extract_article_content(url)
            if not article_content:
                return
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 심층적이고 객관적인 뉴스 분석 전문가입니다. 기사를 명확하고 전문적으로 요약하고, 깊이 있는 맥락과 인사이트를 제공하세요."
                    },
                    {
                        "role": "user", 
                        "content": f"""기사를 다음 형식으로 상세히 분석해주세요:

📄 요약 (5-7줄):
- 기사의 핵심 내용을 정확하고 간결하게 정리
- 주요 사실과 주요 등장인물 포함
- 배경과 맥락을 명확히 설명

🔍 심층 인사이트 (4-5단락):
- 기사의 숨겨진 의미와 광범위한 영향 분석
- 사회적, 경제적, 정치적 맥락에서 해석
- 예상되는 장기적 결과와 잠재적 파급 효과
- 관련 트렌드 및 배경 설명
- 다양한 관점에서의 해석

분석 대상 기사: {article_content}"""
                    }
                ],
                max_tokens=4000
            )
            
            result = response.choices[0].message.content
            logging.info(f"API 응답 받음: {len(result)} 자")
            
            parts = result.split("🔍 심층 인사이트")
            summary = parts[0].replace("📄 요약:", "").strip()
            insights = parts[1].strip() if len(parts) > 1 else "인사이트를 생성하지 못했습니다."
            
            self.signals.update_summary.emit(summary, insights)
        
        except Exception as e:
            logging.error(f"요약 생성 오류: {e}")
            self.signals.error.emit(str(e))

    def _update_summary_ui(self, summary, insights):
        self.summary_output.setPlainText(summary)
        self.insights_output.setPlainText(insights)

    def refine_summary(self):
        try:
            api_key = self.api_key_input.text()
            refinement = self.refinement_input.text()
            current_summary = self.summary_output.toPlainText()
            
            if not api_key or not refinement:
                self.signals.error.emit("API 키와 개선 의견을 입력해주세요")
                return
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "사용자의 요구에 맞춰 뉴스 기사 요약을 세련되고 정확하게 개선하는 AI 어시스턴트입니다."
                    },
                    {
                        "role": "user", 
                        "content": f"다음 요약을 사용자의 의견에 맞춰 개선해주세요:\n\n현재 요약: {current_summary}\n\n개선 요청: {refinement}"
                    }
                ],
                max_tokens=3000
            )
            
            refined_summary = response.choices[0].message.content
            self.signals.update_refined.emit(refined_summary)
        
        except Exception as e:
            self.signals.error.emit(str(e))

    def _update_refined_summary(self, refined_summary):
        self.summary_output.setPlainText(refined_summary)

    def _show_error(self, message):
        QMessageBox.critical(self, "오류", message)

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
