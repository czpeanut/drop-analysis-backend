from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ✅ 確保前端可以存取 API

# 假資料 - 學校清單
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
        new_school = {"id": new_id, "name": data["name"], "minScore": int(data["minScore"])}
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
        print("🔵 收到查詢請求:", data)  # ✅ 檢查後端是否有收到數據

        # 確保請求內包含 score，且是整數
        if "score" not in data:
            print("❌ 錯誤: 缺少 score 參數")
            return jsonify({"error": "請提供有效的數字分數"}), 400
        
        if not isinstance(data["score"], int):
            print("❌ 錯誤: score 不是數字，嘗試轉換")
            try:
                data["score"] = int(data["score"])  # 嘗試轉換為整數
            except ValueError:
                return jsonify({"error": "分數必須是數字"}), 400

        user_score = data["score"]
        matched_schools = [s for s in schools if user_score >= s["minScore"]]

        print("🔵 符合條件的學校:", matched_schools)  # ✅ 確保篩選結果正確

        return jsonify(matched_schools)
    except Exception as e:
        print("❌ 內部錯誤:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
