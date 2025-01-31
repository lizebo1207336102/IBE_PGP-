import base64
import struct

def decode_pgp_public_key(armored_key):
    # PGP ヘッダーとフッターを除去
    armored_key = armored_key.strip()
    armored_key = armored_key.replace("-----BEGIN PGP PUBLIC KEY BLOCK-----", "")
    armored_key = armored_key.replace("-----END PGP PUBLIC KEY BLOCK-----", "")
    armored_key = armored_key.replace("\n", "").replace(" ", "")

    # Base64 デコード
    binary_data = base64.b64decode(armored_key)

    return binary_data

def parse_pgp_binary(binary_data):
    index = 0
    
    # 公開鍵パケット（Tag 6, 旧形式 0x99 または新形式 0x06）
    packet_tag = binary_data[index]  # 1 バイト
    if packet_tag != 0x99 and packet_tag != 0x06:
        raise ValueError(f"Unexpected packet tag: {packet_tag}")
    index += 1
    
    # パケット長
    packet_length = binary_data[index]  # 1 バイト（簡単のため 1 バイトのみ想定）
    index += 1
    
    # バージョン
    version = binary_data[index]  # 1 バイト
    index += 1
    
    # 作成時刻
    creation_time = struct.unpack(">I", binary_data[index:index+4])[0]  # 4 バイト
    index += 4

    # 公開鍵アルゴリズム
    pubkey_algorithm = binary_data[index]  # 1 バイト
    index += 1
    
    # 公開鍵材料（19バイト）
    public_key_material = binary_data[index:index+19]
    index += 19

    # ユーザーIDパケット（Tag 13, `0x0D`）
    user_id_tag = binary_data[index]  # 1 バイト
    if user_id_tag != 0x0D:
        raise ValueError(f"Unexpected user ID tag: {user_id_tag}")
    index += 1

    # ユーザーID長
    user_id_length = binary_data[index]  # 1 バイト
    index += 1

    # ユーザーID
    user_id = binary_data[index:index+user_id_length].decode("utf-8")
    index += user_id_length

    return {
        "packet_tag": packet_tag,
        "packet_length": packet_length,
        "version": version,
        "creation_time": creation_time,
        "pubkey_algorithm": pubkey_algorithm,
        "public_key_material": public_key_material.hex(),
        "user_id_tag": user_id_tag,
        "user_id_length": user_id_length,
        "user_id": user_id
    }

# 例: 生成した PGP 公開鍵をデコード
armored_key = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

BhoEZ5tHOmQCBK43AgLlkQIFKx0CA8NyAgPNGg0bbGl6ZWJvIDxsaXplYm9nbUBn
bWFpbC5jb20+

-----END PGP PUBLIC KEY BLOCK-----
"""

# バイナリデータに戻す
binary_data = decode_pgp_public_key(armored_key)

# 解析
parsed_data = parse_pgp_binary(binary_data)

# 結果を表示
for key, value in parsed_data.items():
    print(f"{key}: {value}")
