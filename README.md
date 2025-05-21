# Drug Interaction Checker

약물 상호작용을 확인할 수 있는 웹 애플리케이션입니다. FDA의 공개 API를 활용하여 약물 정보를 검색하고, 상호작용을 확인할 수 있습니다.

## 주요 기능

- 약물 검색 및 상세 정보 조회
- 약물 간 상호작용 확인
- 부작용 정보 검색
- 리콜/경고 정보 검색
- FDA 승인 정보 검색
- 다국어 지원 (한국어, 영어, 일본어, 중국어, 포르투갈어)

## 기술 스택

- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask)
- API: FDA OpenFDA API
- 번역: Google Cloud Translation API

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd submachine
```

2. Python 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정합니다:
```
FDA_API_KEY=your_fda_api_key
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key
```

## 실행 방법

1. 서버 실행
```bash
python app.py
```

2. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 사용 방법

1. 약물 검색
   - 검색창에 약물명을 입력 (영문)
   - 검색 결과에서 원하는 약물 선택

2. 상호작용 확인
   - 두 개의 약물을 선택
   - "상호작용 확인" 버튼 클릭
   - 상호작용 정보 확인

3. 추가 기능
   - 부작용 검색
   - 리콜/경고 정보 검색
   - FDA 승인 정보 검색

## 주의사항

- 이 애플리케이션은 참고용 정보만을 제공합니다.
- 실제 약물 복용 전 반드시 의사나 약사와 상담하세요.
- FDA 데이터를 기반으로 하며, 자동 번역된 정보가 포함될 수 있습니다.

## 라이선스

MIT License

## 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 