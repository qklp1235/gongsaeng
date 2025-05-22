import json
import os
from druginteraction import (
    translate_drug_name,
    search_drugs,
    fetch_openfda_label,
    extract_label_info,
    translate_to_korean
)

# 자주 사용되는 약물 목록 (예시)
COMMON_DRUGS = [
    "aspirin", "ibuprofen", "acetaminophen", "amoxicillin", "metformin",
    "atorvastatin", "lisinopril", "levothyroxine", "omeprazole", "metoprolol",
    "아스피린", "이부프로펜", "타이레놀", "아목시실린", "메트포르민",
    "아토르바스타틴", "리시노프릴", "레보티록신", "오메프라졸", "메토프롤롤"
]

def generate_drug_data():
    drugs_data = {}
    
    for drug_name in COMMON_DRUGS:
        print(f"Processing {drug_name}...")
        eng_name = translate_drug_name(drug_name)
        if not eng_name:
            continue
            
        label = fetch_openfda_label(eng_name)
        if not label:
            continue
            
        info = extract_label_info(label, eng_name)
        
        # 번역
        translated_info = {
            "drug": translate_to_korean(info["drug"]),
            "brand_name": translate_to_korean(info["brand_name"]),
            "indications": translate_to_korean(info["indications"]),
            "classification": translate_to_korean(info["classification"]),
            "dosage": translate_to_korean(info["dosage"]),
            "adverse_reactions": translate_to_korean(info["adverse_reactions"]),
            "interactions": translate_to_korean(info["interactions"]),
            "warnings": translate_to_korean(info["warnings"]),
            "precautions": translate_to_korean(info["precautions"])
        }
        
        # 영어 이름과 한글 이름 모두 키로 저장
        drugs_data[eng_name.lower()] = translated_info
        if drug_name != eng_name:
            drugs_data[drug_name.lower()] = translated_info
    
    return drugs_data

def generate_interaction_data(drugs_data):
    interactions = {}
    drug_names = list(drugs_data.keys())
    
    for i, drug1 in enumerate(drug_names):
        for drug2 in drug_names[i+1:]:
            key = f"{drug1.lower()}_{drug2.lower()}"
            reverse_key = f"{drug2.lower()}_{drug1.lower()}"
            
            # 이미 처리된 조합은 건너뛰기
            if key in interactions or reverse_key in interactions:
                continue
                
            print(f"Checking interaction between {drug1} and {drug2}...")
            
            # 상호작용 정보 추출
            info1 = drugs_data[drug1]
            info2 = drugs_data[drug2]
            
            has_interaction = any(
                info1[field] not in ["상호작용 정보 없음", "주의사항 없음", "예방조치 없음"] or
                info2[field] not in ["상호작용 정보 없음", "주의사항 없음", "예방조치 없음"]
                for field in ["interactions", "warnings", "precautions"]
            )
            
            interactions[key] = {
                "has_interaction": has_interaction,
                "drug1": {
                    "name": info1["drug"],
                    "interactions": info1["interactions"],
                    "warnings": info1["warnings"],
                    "precautions": info1["precautions"]
                },
                "drug2": {
                    "name": info2["drug"],
                    "interactions": info2["interactions"],
                    "warnings": info2["warnings"],
                    "precautions": info2["precautions"]
                }
            }
    
    return interactions

def main():
    # 데이터 디렉토리 생성
    os.makedirs("static/data", exist_ok=True)
    
    # 약물 데이터 생성
    print("Generating drug data...")
    drugs_data = generate_drug_data()
    with open("static/data/drugs.json", "w", encoding="utf-8") as f:
        json.dump(drugs_data, f, ensure_ascii=False, indent=2)
    
    # 상호작용 데이터 생성
    print("Generating interaction data...")
    interactions = generate_interaction_data(drugs_data)
    with open("static/data/interactions.json", "w", encoding="utf-8") as f:
        json.dump(interactions, f, ensure_ascii=False, indent=2)
    
    print("Done! Static data has been generated.")

if __name__ == "__main__":
    main() 