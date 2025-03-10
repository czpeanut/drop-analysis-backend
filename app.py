from flask import Flask, request, jsonify

app = Flask(__name__)

# 假資料（確保與你的原始後端一致）
schools = [
    {"id": 1, "name": "台南一中", "minScore": 30},
    {"id": 2, "name": "台中女中", "minScore": 29},
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
    data = request.json
    if not data or "name" not in data or "minScore" not in data:
        return jsonify({"error": "缺少必要欄位"}), 400

    new_id = max([s["id"] for s in schools]) + 1 if schools else 1
    new_school = {"id": new_id, "name": data["name"], "minScore": data["minScore"]}
    schools.append(new_school)
    return jsonify(new_school), 201

# 刪除學校
@app.route("/schools/<int:school_id>", methods=["DELETE"])
def delete_school(school_id):
    global schools
    schools = [s for s in schools if s["id"] != school_id]
    return jsonify({"message": f"學校 ID {school_id} 已刪除"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
