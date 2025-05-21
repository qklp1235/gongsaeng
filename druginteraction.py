import requests
import time
from deep_translator import GoogleTranslator

# 번역기 인스턴스
translator = GoogleTranslator(source='auto', target='ko')
eng_translator = GoogleTranslator(source='ko', target='en')

def translate_drug_name(name):
    name = name.strip().lower()
    if all(ord(c) < 128 for c in name):
        return name
    try:
        eng_name = eng_translator.translate(name)
        return eng_name.lower() if eng_name else None
    except Exception:
        return None

def search_drugs(query):
    url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{query}\"+openfda.brand_name:\"{query}\"&limit=20"
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("results", [])
        time.sleep(1)
        unique_drugs = set()
        for drug in results:
            brand_names = drug.get("openfda", {}).get("brand_name", [])
            generic_names = drug.get("openfda", {}).get("generic_name", [])
            unique_drugs.update(brand_names + generic_names)
        return list(unique_drugs)
    except requests.exceptions.RequestException as e:
        print(f"[API 오류] 약물 검색 실패 ({query}): {e}")
        return []

def fetch_openfda_label(drug_name):
    url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{drug_name}\"+openfda.brand_name:\"{drug_name}\"&limit=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("results", [])
        time.sleep(1)
        return results[0] if results else None
    except requests.exceptions.RequestException as e:
        print(f"[API 오류] OpenFDA API 호출 실패 ({drug_name}): {e}")
        return None

def translate_to_korean(text):
    if not text or text in ["정보 없음", "부작용 정보 없음", "분류 정보 없음"]:
        return text

    def split_sentences(text):
        sentences = []
        for line in text.split("\n"):
            for part in (line.split(". ") if ". " in line else [line]):
                if len(part) > 120:
                    for i in range(0, len(part), 120):
                        sentences.append(part[i:i+120])
                else:
                    sentences.append(part)
        return [s.strip() for s in sentences if s.strip()]

    for _ in range(2):
        try:
            translated = translator.translate(str(text))
            if translated:
                return translated
        except Exception:
            pass

    if len(text) > 60:
        sentences = split_sentences(text)
        translated_sentences = []
        for sentence in sentences:
            try:
                translated = translator.translate(sentence)
                translated_sentences.append(translated if translated else sentence)
            except Exception:
                translated_sentences.append(sentence)
        return " ".join(translated_sentences)

    return f"(⚠️ 번역 실패) {text}"

def translate_multiple_texts(texts):
    return [translate_to_korean(t) for t in texts]

def extract_label_info(label, input_name):
    def get_field(field, default="정보 없음"):
        value = label.get(field, default)
        if isinstance(value, list) and value:
            return value[0]
        return str(value) if value else default

    if not isinstance(label, dict):
        return {
            "drug": input_name,
            "brand_name": input_name,
            "indications": "정보 없음",
            "classification": "분류 정보 없음",
            "dosage": "정보 없음",
            "adverse_reactions": "부작용 정보 없음",
            "interactions": "상호작용 정보 없음",
            "warnings": "주의사항 없음",
            "precautions": "예방조치 없음",
        }

    drug_name = label.get("openfda", {}).get("generic_name", [input_name])[0] or input_name
    brand_name = get_field("openfda.brand_name", input_name)
    classification = get_field("openfda.substance_name", "분류 정보 없음")

    return {
        "drug": drug_name,
        "brand_name": brand_name,
        "indications": get_field("indications_and_usage"),
        "classification": classification,
        "dosage": get_field("dosage_and_administration"),
        "adverse_reactions": get_field("adverse_reactions", "부작용 정보 없음"),
        "interactions": get_field("drug_interactions", "상호작용 정보 없음"),
        "warnings": get_field("warnings", "주의사항 없음"),
        "precautions": get_field("precautions", "예방조치 없음"),
    }

def summarize_text(text, max_length=200):
    if not isinstance(text, str) or not text:
        return "정보 없음"
    if len(text) <= max_length:
        return text
    try:
        summary = ""
        for sentence in text.split(". "):
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        return summary.strip() + "..."
    except Exception:
        return text[:max_length] + "..."

def check_interaction(drug1, drug2, label1, label2):
    info1 = extract_label_info(label1, drug1)
    info2 = extract_label_info(label2, drug2)

    texts = [info1["interactions"], info1["warnings"], info1["precautions"],
             info2["interactions"], info2["warnings"], info2["precautions"]]

    translated = translate_multiple_texts(texts)

    info1_translated = dict(zip(["interactions", "warnings", "precautions"], translated[:3]))
    info2_translated = dict(zip(["interactions", "warnings", "precautions"], translated[3:]))

    has_interaction = any(v not in ["상호작용 정보 없음", "주의사항 없음", "예방조치 없음"] for v in translated)

    return info1, info2, info1_translated, info2_translated, has_interaction

def print_info_block(info, translated, index):
    print(f"\n📦 [{index+1}번 약물 정보] {info['drug']}")
    print(f"- 상품명: {translate_to_korean(info['brand_name'])}")
    print(f"- 용도: {summarize_text(translate_to_korean(info['indications']))}")
    print(f"- 분류: {translate_to_korean(info['classification'])}")
    print(f"- 복용법: {summarize_text(translate_to_korean(info['dosage']))}")
    print(f"- 부작용: {summarize_text(translate_to_korean(info['adverse_reactions']))}")

def print_interaction_result(drug1, drug2, info1, info2, trans1, trans2, has_interaction):
    print("\n🚨 [상호작용 결과]")
    if has_interaction:
        print(f"⚠️ '{drug1}' 와 '{drug2}' 간 주의가 필요합니다.")
        for i, (info, trans) in enumerate([(info1, trans1), (info2, trans2)]):
            for k, label in [("interactions", "상호작용"), ("warnings", "주의사항"), ("precautions", "예방조치")]:
                if trans[k] not in ["상호작용 정보 없음", "주의사항 없음", "예방조치 없음"]:
                    print(f"- {info['drug']} {label}: {summarize_text(trans[k])}")
            if i == 0:
                print("----------------")
    else:
        print(f"✅ '{drug1}' 와 '{drug2}' 간 알려진 상호작용이 없습니다.")
    print("\n※ 참고용 정보이며, 실제 복용 전 의사 또는 약사와 상담하세요.")

def main():
    print("💊 약물 정보 조회기 - 출처: 미국 식품의약국(OpenFDA)")
    drug1_input = input("첫 번째 약물 이름 (한글 또는 영문): ").strip()
    drug2_input = input("두 번째 약물 이름 (한글 또는 영문): ").strip()

    drug1 = translate_drug_name(drug1_input)
    drug2 = translate_drug_name(drug2_input)

    if not drug1 or not drug2:
        print("\n❗ 약물명 번역 실패 또는 알 수 없는 입력입니다.")
        for name in [drug1_input, drug2_input]:
            suggestions = search_drugs(name)
            if suggestions:
                print(f"🔍 '{name}' 관련 제안: {', '.join(suggestions[:5])}")
        return

    if drug1 == drug2:
        print("❗ 서로 다른 약물을 입력해주세요.")
        return

    print("\n🔍 약물 정보 조회 중...")
    label1 = fetch_openfda_label(drug1)
    label2 = fetch_openfda_label(drug2)

    if not label1 or not label2:
        print("\n❗ 약물 정보 조회 실패")
        for name in [drug1, drug2]:
            if not fetch_openfda_label(name):
                print(f"🔍 '{name}' 관련 제안:")
                suggestions = search_drugs(name)
                if suggestions:
                    print(f"  → {', '.join(suggestions[:5])}")
        return

    info1, info2, trans1, trans2, has_interaction = check_interaction(drug1, drug2, label1, label2)
    print_info_block(info1, trans1, 0)
    print_info_block(info2, trans2, 1)
    print_interaction_result(drug1, drug2, info1, info2, trans1, trans2, has_interaction)

if __name__ == "__main__":
    main()