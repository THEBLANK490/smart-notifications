import hashlib

def get_device_fingerprint(ip, user_agent):
    raw = f"{ip}_{user_agent}"
    return hashlib.sha256(raw.encode()).hexdigest()