import base64
import binascii

# 1️⃣ 暗号化されたAES鍵 (16進文字列)
hex_encrypted_aes_key = "5150005603520107015453560509075309540900540054515452570303030609535209530150020355080503090851020253520908060053515452550502520900515402530501025601575201070704040653030705015256070952085109560400505302030402060602000202020505050601540508050552575651080204"
print(hex_encrypted_aes_key)
# 2️⃣ 16進文字列をバイト列 (bytes) に変換
encrypted_aes_key_bytes = binascii.unhexlify(hex_encrypted_aes_key)
print("AES鍵 (バイナリ形式):", encrypted_aes_key_bytes)

# 3️⃣ Base64 エンコードして ASCII 文字列に変換
base64_encoded_key = base64.b64encode(encrypted_aes_key_bytes).decode('ascii')
print("Base64 エンコード (ASCII 文字列):", base64_encoded_key)

# 4️⃣ Base64 の ASCII 文字列を元のバイナリデータに復元
decoded_bytes = base64.b64decode(base64_encoded_key.encode('ascii'))
print("復元されたAES鍵 (バイナリ形式):", decoded_bytes)

# 5️⃣ 復元したバイナリデータを 16進表現に戻す (元の鍵と一致するか確認)
restored_hex_key = binascii.hexlify(decoded_bytes).decode()
print("復元されたAES鍵 (16進文字列):", restored_hex_key)

#  変換前後の一致を確認
assert hex_encrypted_aes_key == restored_hex_key, "❌ エラー: 復元されたAES鍵が元と一致しません！"
print(" AES鍵の復元が成功しました！")
