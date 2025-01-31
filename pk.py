import time
import struct
import base64
import datetime

def unix_to_human_readable(unix_time):
    """UNIX 時刻を YYYY-MM-DD HH:MM:SS に変換"""
    return datetime.datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
def encode_base64(data):
    """データをBase64エンコードする"""
    return base64.b64encode(data).decode('utf-8')

def decode_base64(encoded_data):
    """Base64データをデコードしてバイナリに戻す"""
    return base64.b64decode(encoded_data.replace("-----BEGIN PGP PUBLIC KEY BLOCK-----", "")
                                        .replace("-----END PGP PUBLIC KEY BLOCK-----", "")
                                        .replace("\n", "").strip())

def create_custom_pgp_public_key():
    # **パケットタグ（Tag 6, 新形式）**
    packet_tag = b'\x06'  # 公開鍵パケット

    # **バージョン（通常 4）**
    version = b'\x04'

    # **作成時刻（4 バイト, ビッグエンディアン）**
    timestamp = int(time.time())  # 現在のUNIX時刻
    creation_time = struct.pack(">I", timestamp)  # 4 バイト

    # **公開鍵アルゴリズム（100, IBE 用）**
    pubkey_algorithm = b'\x64'

    # **公開鍵材料（20バイト）**
    def pack_value(value):
        """1バイトの長さフィールド + 3バイトのデータ"""
        return b'\x03' + struct.pack(">I", value)[1:]  # 3バイトのみ使用

    ppub_p1 = pack_value(306743)
    ppub_p2 = pack_value(189841)
    p_value  = pack_value(338717)
    P1_value = pack_value(246642)
    P2_value = pack_value(249114)

    public_key_material = ppub_p1 + ppub_p2 + p_value + P1_value + P2_value  # **合計20バイト**

    # **パケット長の計算**
    packet_length_value = len(packet_tag + version + creation_time + pubkey_algorithm + public_key_material)
    packet_length = struct.pack(">B", packet_length_value)  # 1 バイト

    # **公開鍵パケット**
    public_key_packet = packet_tag + packet_length + version + creation_time + pubkey_algorithm + public_key_material

    # **ユーザーIDパケット（Tag 13, 可変長）**
    user_id_packet_tag = b'\x0D'  # **Tag 13 (0x0D)**
    user_id = b'lizebo <lizebogm@gmail.com>'
    user_id_length = struct.pack(">B", len(user_id))  # **ユーザーIDのバイト数を1バイトで格納**
    user_id_packet = user_id_packet_tag + user_id_length + user_id

    # **PGP ASCII Armor 形式の公開鍵を生成**
    key_data = public_key_packet + user_id_packet
    base64_key = encode_base64(key_data)

    # **出力フォーマットを整える**
    armored_key = "-----BEGIN PGP PUBLIC KEY BLOCK-----\n\n"
    armored_key += "\n".join([base64_key[i:i+64] for i in range(0, len(base64_key), 64)])
    armored_key += "\n\n-----END PGP PUBLIC KEY BLOCK-----"

    return armored_key

def parse_pgp_binary(binary_data):
    """PGP 公開鍵のバイナリデータを解析し、p, Ppub, P を抽出"""
    index = 0

    # **公開鍵パケット（Tag 6, 新形式 0x06）**
    packet_tag = binary_data[index]  # 1 バイト
    if packet_tag != 0x06:
        raise ValueError(f"Unexpected packet tag: {packet_tag}")
    index += 1

    # **パケット長**
    packet_length = binary_data[index]  # 1 バイト
    index += 1

    # **バージョン**
    version = binary_data[index]  # 1 バイト
    index += 1

    # **作成時刻**
    creation_time = struct.unpack(">I", binary_data[index:index+4])[0]  # 4 バイト
    index += 4

    # **公開鍵アルゴリズム**
    pubkey_algorithm = binary_data[index]  # 1 バイト
    index += 1

    # **公開鍵材料（20バイト）を解析**
    def extract_value(data, start):
        """公開鍵データを解析して整数値を取得"""
        size = data[start]  # 最初の1バイトがデータサイズ（常に 0x03）
        value = int.from_bytes(data[start+1:start+1+size], "big")  # 残りが値（3バイト）
        return value, start + 1 + size

    ppub_p1, index = extract_value(binary_data, index)
    ppub_p2, index = extract_value(binary_data, index)
    p_value, index = extract_value(binary_data, index)
    P1_value, index = extract_value(binary_data, index)
    P2_value, index = extract_value(binary_data, index)

    # **ユーザーIDパケット（Tag 13, `0x0D`）**
    user_id_tag = binary_data[index]  # 1 バイト
    if user_id_tag != 0x0D:
        raise ValueError(f"Unexpected user ID tag: {user_id_tag}")
    index += 1

    # **ユーザーID長**
    user_id_length = binary_data[index]  # 1 バイト
    index += 1

    # **ユーザーID**
    user_id = binary_data[index:index+user_id_length].decode("utf-8")
    index += user_id_length

    return {
        "packet_tag": packet_tag,
        "packet_length": packet_length,
        "version": version,
        "creation_time": unix_to_human_readable(creation_time),
        "pubkey_algorithm": pubkey_algorithm,
        "ppub_p1": ppub_p1,
        "ppub_p2": ppub_p2,
        "p": p_value,
        "P1": P1_value,
        "P2": P2_value,
        "user_id_tag": user_id_tag,
        "user_id_length": user_id_length,
        "user_id": user_id
    }

# **PGP 公開鍵を生成**
pgp_public_key = create_custom_pgp_public_key()

# **公開鍵を表示**
print(pgp_public_key)

# **復元（Base64 からバイナリデータに戻す）**
binary_data = decode_base64(pgp_public_key)

# **バイナリデータを解析**
parsed_data = parse_pgp_binary(binary_data)

# **解析結果を表示**
print("\n--- PGP 公開鍵の解析結果 ---")
for key, value in parsed_data.items():
    print(f"{key}: {value}")
