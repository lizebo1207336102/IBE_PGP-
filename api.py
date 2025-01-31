from flask import Flask, jsonify, request
from boneh_chiff import findPoint2, hash, hash3, xor, EllipticCurve, ModP, Ciphertext
import random
import binascii
import ellipticCurve
import ellipticCurveMod
import modular
import finiteField
import polynomial
import WeilPairing
from flask_cors import CORS
EllipticCurve2=ellipticCurve.EllipticCurve
ModP = modular.ModP
FiniteField = finiteField.FiniteField
Polynomial = polynomial.Polynomial
ModifWeil = WeilPairing.ModifWeilPairing
Point2=ellipticCurve.Point
EllipticCurve=ellipticCurveMod.EllipticCurve
Point=ellipticCurveMod.Point
Infinity=ellipticCurveMod.Infinity
app = Flask(__name__)
CORS(app)  # 全てのオリジンを許可（または制限をかける）

# システムのセットアップ
l = 56453  # 秩（群の位数）
p = 6 * l - 1  # 素数 p を計算
C = EllipticCurve(ModP(0, p), ModP(1, p))  # 楕円曲線の生成

# マスター秘密鍵（テスト用）
s = 13
P = findPoint2(C, l, p)  # 楕円曲線上の基点
Ppub = s * P  # 公開鍵 Ppub = s * P
Fp2 = FiniteField(p,2, Polynomial([ModP(1,p),ModP(1,p),ModP(1,p)],p)) #for l=56453
b = Fp2([0,1]) #for l=56453
E2 = EllipticCurve2( Fp2([0]), Fp2([1]), Fp2)


@app.route('/public_params', methods=['GET'])
def get_public_params():
    """ 公開パラメータを取得するエンドポイント """
    public_params = {
        "l": l,                     # パラメータ l
        "p": p,                     # パラメータ p
        "Ppub_x": Ppub.x.n,          # 公開鍵パラメータのX座標
        "Ppub_y": Ppub.y.n,          # 公開鍵パラメータのY座標
        "Curve_a": C.a.n,            # 楕円曲線のパラメータ a
        "Curve_b": C.b.n             # 楕円曲線のパラメータ b
    }
    return jsonify(public_params)

@app.route('/generate_pubkey', methods=['POST'])
def generate_pubkey():
    """ ユーザーIDに基づく公開鍵を生成 """
    data = request.json
    ID = data.get('ID')

    if not ID:
        return jsonify({"error": "ID が必要です"}), 400

    # IDを楕円曲線上の点に変換
    QID = hash(ID, C, p, P, l)

    # 公開鍵としてQIDを返す
    public_key = {
        "QID_x": QID.x.n,
        "QID_y": QID.y.n
    }

    return jsonify(public_key)

@app.route('/encrypt', methods=['POST'])
def encrypt_message():
    """ メッセージの暗号化エンドポイント """
    data = request.json
    ID = data.get('ID')
    M = data.get('message')

    if not ID or not M:
        return jsonify({"error": "IDとメッセージの両方が必要です"}), 400

    # IDの楕円曲線上のポイント QID の生成
    QID = hash(ID, C, p, P, l)

    # 秘密鍵を用いたDIDの生成
    DID = s * QID

    # ランダム値 r の生成
    r = random.randint(1, l - 1)
    QIDAlice = hash(ID,C,p, P, l)
    r = int(7)
    QIDAlice2 = Point2(E2, Fp2([QIDAlice.x.n]), Fp2([QIDAlice.y.n]))
    Ppub2 = Point2(E2, Fp2([Ppub.x.n]), Fp2([Ppub.y.n]))

    # gID の計算
    gID = ModifWeil(QIDAlice2, Ppub2, l , b)

    # メッセージの暗号化（XOR処理）
    lengthMessage = len(M)
    b1 = bytearray(M.encode('utf-8'))
    hash_1 = hash3(gID**(r), lengthMessage)
    xor1 = xor(b1,hash_1)
    # 暗号文の生成
    print("The message after encryption in bytes: ")
    print(xor1)
    #create a hex representation of the encrypted message. this way, it is easier to communicate to a third party
    #and independent of the machine which is running.
    decoded = binascii.hexlify(xor1)
     # 結果を表示（デバッグ用）
    print("暗号文の16進文字列:", str(decoded)[2:-1])

    # Flaskのレスポンスとして返す
    return jsonify({
        "encrypted_message": str(decoded)[2:-1]
    })

@app.route('/decrypt', methods=['POST'])
def decrypt_message():
    """復号化処理を行うエンドポイント"""

    data = request.json
    DIDCordX = data.get('DID_x')
    DIDCordY = data.get('DID_y')
    encrypted_message = data.get('ciphertext')

    if not DIDCordX or not DIDCordY or not encrypted_message:
        return jsonify({"error": "DID_x, DID_y, 暗号文のすべてが必要です"}), 400

    try:
        # 楕円曲線上のポイントとしてDIDを生成
        DID = Point2(E2, Fp2([int(DIDCordX)]), Fp2([int(DIDCordY)]))

        # 固定値として設定（cypherA の座標）
        cypherACordX = 240099
        cypherACordY = 283222
        cypherA = Point2(E2, Fp2([cypherACordX]), Fp2([cypherACordY]))

        # 暗号文のデコード
        cypherB = binascii.unhexlify(encrypted_message)

        # 復号キーの計算
        hID = ModifWeil(DID, cypherA, l, b)

        # 復号処理
        decrypted_hash = hash3(hID, len(cypherB))
        decrypted_message = xor(cypherB, decrypted_hash)

        # 復号結果を文字列として返す
        return jsonify({
            "decrypted_message": decrypted_message.decode()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)
