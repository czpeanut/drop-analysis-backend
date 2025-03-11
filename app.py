from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ✅ 確保前端可以存取 API

# 假資料
schools = [
    {"id": 1, "name": "台北一中", "minScore": 80},
    {"id": 2, "name": "台中女中", "minScore": 75},
    {"id": 3, "name": "台南一中", "minScore": 70},
]

@app.route("/")
def home():
    return jsonify({"message": "落點分析後端 Flask API 運行中"})

# 取得學校清單
@app.route("/schools", methods=["GET"])
def get_schools():
    return jsonify(schools)

# 新增學校
@app.route("/schools", methods=["POST"])
def add_school():
    try:
        data = request.json
        if not data or "name" not in data or "minScore" not in data:
            return jsonify({"error": "缺少必要欄位"}), 400

        new_id = max([s["id"] for s in schools]) + 1 if schools else 1
        new_school = {"id": new_id, "name": data["name"], "minScore": data["minScore"]}
        schools.append(new_school)
        return jsonify(new_school), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 刪除學校
@app.route("/schools/<int:school_id>", methods=["DELETE"])
def delete_school(school_id):
    global schools
    schools = [s for s in schools if s["id"] != school_id]
    return jsonify({"message": f"學校 ID {school_id} 已刪除"})

# 根據分數查詢可錄取學校
@app.route("/check", methods=["POST"])
def check_schools():
    try:
        data = request.json
        if "score" not in data:
            return jsonify({"error": "請提供分數"}), 400

        user_score = int(data["score"])
        matched_schools = [s for s in schools if user_score >= s["minScore"]]

        return jsonify(matched_schools)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
