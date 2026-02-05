# Copyright 2026 0ut0flin3
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ed25519_ext import SigningKey
import base64
import requests
import struct
import secrets
from typing import Dict, Any
import hashlib

TESTNET_PASSPHRASE = "Test SDF Network ; September 2015"
HORIZON_URL = "https://horizon-testnet.stellar.org"
NETWORK_ID = hashlib.sha256(TESTNET_PASSPHRASE.encode()).digest()

ENVELOPE_TYPE_TX         = b'\x00\x00\x00\x02'
PUBLIC_KEY_TYPE_ED25519  = b'\x00\x00\x00\x00'
SIGNATURE_HINT_LENGTH    = 4
VERSION_BYTE_ACCOUNT_ID = 6 << 3
VERSION_BYTE_SECRET_SEED = 18 << 3

def crc16_xmodem(data: bytes) -> int:
    crc = 0x0000
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def strkey_encode(version_byte: int, payload: bytes) -> str:
    data = bytes([version_byte]) + payload
    checksum = struct.pack("<H", crc16_xmodem(data))
    encoded = base64.b32encode(data + checksum)
    return encoded.decode("ascii")

def keypair_from_seed(seed):
    sk = SigningKey(seed)
    vk_obj = sk.get_verifying_key()
    vk = vk_obj.to_bytes()
    secret = strkey_encode(VERSION_BYTE_SECRET_SEED, seed)
    public_key = strkey_encode(VERSION_BYTE_ACCOUNT_ID, vk)
    return public_key, secret

def enable_id(fr0g_id,fr0g_secret):
    address=fr0g_id[4:][::-1].upper()
    url = f"https://friendbot.stellar.org?addr={address}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
         "Accept": "application/json",
    }
    requests.get(url, headers=headers)
    set_value(f':{fr0g_id}:',b'\x01', fr0g_secret)

def is_valid_identifier(s: str) -> bool:
    return s.isascii() and all(c.isdigit() or c.islower() or c == '_' for c in s)

def stellar2fr0gID(stellar_address):
    return 'fr0g' + stellar_address.lower()[::-1]

def fr0gID2stellar(fr0g_id):
    return fr0g_id[4:][::-1].upper()

def fr0gsecret2stellar(fr0g_secret):
    return strkey_encode(VERSION_BYTE_SECRET_SEED, bytes.fromhex(fr0g_secret))

def random_keypair(enabled=False):
    seed = secrets.token_bytes(32)
    stellar_pubkey, stellar_secret = keypair_from_seed(seed)
    fr0g_id = stellar2fr0gID(stellar_pubkey)
    if enabled:
       try: 
           enable_id(fr0g_id,seed.hex())
       except:
              raise Exception('''Connection error: Fr0g ID was created but not initialized''')
    return fr0g_id, seed.hex()         

def chunk(inp: bytes):
    inp = list(inp)
    while len(inp) % 64 != 0:
        inp.append(0xFF)
    n_chunks = int(len(inp) / 64)
    j = 0
    i = 64
    out = []
    for x in range(0, n_chunks):
        out.append(bytes(inp[j:i]))
        j += 64
        i += 64
    return out

def get_sequence_number(account_id):
    r = requests.get(f"{HORIZON_URL}/accounts/{account_id}")
    seq = int(r.json()["sequence"]) if r.ok else 0
    return seq

def create_empty_transaction(source_account: str, sequence: int) -> Dict[str, Any]:
    tx = {
        "source_account": source_account,
        "sequence": sequence,
        "fee": 100,
        "time_bounds": None,
        "memo": {"type": "none"},
        "operations": [],
        "network_id": NETWORK_ID,
        "tx_xdr": None,
        "tx_hash": None
    }
    return tx

def append_manage_data_op(
    tx: Dict[str, Any],
    key: str,
    value: bytes | str | None = None
) -> Dict[str, Any]:
    if len(key) > 64:
        raise ValueError("ManageData key max length = 64 bytes")
    if isinstance(value, str):
        value = value.encode("utf-8")
    if value is not None and len(value) > 64:
        raise ValueError("ManageData value max length = 64 bytes")
    op = {
        "type": "manage_data",
        "data": {
            "key": key,
            "value": value
        }
    }
    tx["operations"].append(op)
    return tx

def sign_transaction(tx: Dict[str, Any], secret_seed: str) -> Dict[str, Any]:
    secret_seed = secret_seed.upper().replace(" ", "").replace("-", "")
    padded = secret_seed + "=" * ((8 - len(secret_seed) % 8) % 8)
    raw = base64.b32decode(padded)
    if len(raw) != 35:
        raise ValueError("Secret seed non valido")
    secret_seed_bytes = raw[1:33]
    signing_key = SigningKey(secret_seed_bytes)
    public_key_bytes = signing_key.get_verifying_key().to_bytes()
    source_account_xdr = PUBLIC_KEY_TYPE_ED25519 + public_key_bytes
    fee_xdr = struct.pack(">I", tx["fee"] * len(tx["operations"]))
    seq_num_xdr = struct.pack(">Q", tx["sequence"])
    memo_xdr = struct.pack(">I", 0)
    time_bounds_xdr = struct.pack(">I", 0)
    ops_xdr = b""
    for op in tx["operations"]:
        op_source_xdr = struct.pack(">I", 0)
        key_bytes = op["data"]["key"].encode("ascii")
        key_xdr = struct.pack(">I", len(key_bytes)) + key_bytes + b"\x00" * ((4 - len(key_bytes) % 4) % 4)
        if op["data"]["value"] is None:
            value_xdr = struct.pack(">I", 0)
        else:
            val = op["data"]["value"]
            value_xdr = (
                struct.pack(">I", 1) +
                struct.pack(">I", len(val)) +
                val +
                b"\x00" * ((4 - len(val) % 4) % 4)
            )
        ops_xdr += (
            op_source_xdr +
            struct.pack(">I", 10) +
            key_xdr +
            value_xdr
        )
    tx_body_xdr = (
        source_account_xdr +
        fee_xdr +
        seq_num_xdr +
        memo_xdr +
        time_bounds_xdr +
        struct.pack(">I", len(tx["operations"])) +
        ops_xdr +
        struct.pack(">I", 0)
    )
    payload = NETWORK_ID + ENVELOPE_TYPE_TX + tx_body_xdr
    tx_hash = hashlib.sha256(payload).digest()
    signature = signing_key.sign(tx_hash)
    hint = public_key_bytes[-SIGNATURE_HINT_LENGTH:]
    envelope_xdr = (
        tx_body_xdr +
        struct.pack(">I", 1) +
        hint +
        struct.pack(">I", len(signature)) +
        signature
    )
    tx["tx_xdr"] = base64.b64encode(envelope_xdr).decode("ascii")
    tx["tx_hash"] = tx_hash.hex()
    return tx

def submit_transaction(tx: dict, horizon_url: str = HORIZON_URL):
    payload = {"tx": tx["tx_xdr"]}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        f"{horizon_url}/transactions",
        data=payload,
        headers=headers
    )
    if not response.ok:
        print(response.text)
        raise ConnectionError("Errore Horizon")
    return response.json()

def retrieve_data(fr0g_id):
    r = requests.get(f"{HORIZON_URL}/accounts/{fr0gID2stellar(fr0g_id)}")
    r.raise_for_status()
    account_info = r.json()
    data_entries = account_info.get("data", {})
    decoded_entries = {k: base64.b64decode(v).decode("utf-8", errors="ignore") for k, v in data_entries.items()}     
    result = [(key, value) for key, value in decoded_entries.items()]
    return result

def set_value(key:str,value:bytes,fr0g_secret):
    stellar_address,stellar_secret=keypair_from_seed(bytes.fromhex(fr0g_secret))[0]  ,fr0gsecret2stellar(fr0g_secret)
    tx=create_empty_transaction(stellar_address,get_sequence_number(stellar_address)+1)
    tx=append_manage_data_op(tx,key,value)
    tx=sign_transaction(tx,stellar_secret)
    submit_transaction(tx)    

def get_file_count(fr0g_id):
    data=retrieve_data(fr0g_id)
    l=[0]
    for x in data:
        if 'fr0g:f' in x[0]:
           l.append(int(x[0][x[0].find('fr0g:f')+6]))
    file_count=max(l)
    return file_count

def upload(inp:bytes,fr0g_secret,index=0):
    fr0g_id=stellar2fr0gID(keypair_from_seed(bytes.fromhex(fr0g_secret))[0])
    file_count=get_file_count(fr0g_id)
    if index==0:
       file_count=-1    
    chunks=chunk(inp)
    tx=create_empty_transaction(fr0g_id,get_sequence_number(fr0gID2stellar(fr0g_id))+1)
    for x in range(len(chunks)):
        tx=append_manage_data_op(tx, "fr0g:f"+str(file_count+1)+"c"+str(x+1)+":"+str(len(list(inp))),chunks[x])
    tx=sign_transaction(tx,keypair_from_seed(bytes.fromhex(fr0g_secret))[1])
    submit_transaction(tx)

def get_content(fr0g_ID,index=0):
    data=retrieve_data(fr0g_ID)
    n_chunks=[]
    for x in range(len(data)):        
        if data[x][0].startswith("fr0g:f"+str(index)):
           n_chunks.append(int(data[x][0][8]))    
    if len(n_chunks)==0:
       return None
    n_chunks.sort()
    chunks=[]
    for x in range(len(data)):
        for y in n_chunks :
            if data[x][0].startswith("fr0g:f"+str(index)+"c"+str(y)):
               chunks.append(data[x][1])
    return "".join(chunks)
