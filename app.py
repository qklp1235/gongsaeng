from flask import Flask, render_template, request, jsonify
from druginteraction import (
    translate_drug_name, fetch_openfda_label,
    check_interaction, extract_label_info,
    search_drugs
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('druginteraction.html')

@app.route('/search_drug', methods=['POST'])
def search_drug():
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': '검색어를 입력해주세요.'}), 400

    # 한글 입력인 경우 영문으로 번역
    if not all(ord(c) < 128 for c in query):
        translated = translate_drug_name(query)
        if translated:
            query = translated

    # FDA API에서 약물 검색
    results = search_drugs(query)
    
    if not results:
        return jsonify({
            'error': '검색 결과가 없습니다. 다른 검색어를 시도해보세요.'
        }), 404

    return jsonify({
        'results': results[:10]  # 최대 10개 결과만 반환
    })

@app.route('/check_interaction', methods=['POST'])
def check_drug_interaction():
    data = request.get_json()
    drug1_input = data.get('drug1', '').strip()
    drug2_input = data.get('drug2', '').strip()

    if not drug1_input or not drug2_input:
        return jsonify({'error': '약물 이름을 입력해주세요.'}), 400

    drug1 = translate_drug_name(drug1_input)
    drug2 = translate_drug_name(drug2_input)

    if not drug1 or not drug2:
        return jsonify({
            'error': '약물명 번역 실패 또는 알 수 없는 입력입니다.'
        }), 400

    if drug1 == drug2:
        return jsonify({
            'error': '서로 다른 약물을 입력해주세요.'
        }), 400

    label1 = fetch_openfda_label(drug1)
    label2 = fetch_openfda_label(drug2)

    if not label1 or not label2:
        return jsonify({
            'error': '약물 정보를 찾을 수 없습니다.'
        }), 404

    info1, info2, trans1, trans2, has_interaction = check_interaction(
        drug1, drug2, label1, label2
    )

    return jsonify({
        'drug1': drug1,
        'drug2': drug2,
        'info1': info1,
        'info2': info2,
        'trans1': trans1,
        'trans2': trans2,
        'has_interaction': has_interaction
    })

if __name__ == '__main__':
    app.run(debug=True) 