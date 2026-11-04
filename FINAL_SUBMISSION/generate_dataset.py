import os
import hashlib

# FIXED PARAMETERS — do not change, so every group gets byte-identical files
SEED = b"CNS_ISE_GROUP_PROJECT_2026_SEED_42"  # fixed seed as bytes
SIZES_MIB = {'1MiB': 1, '10MiB': 10, '50MiB': 50, '100MiB': 100}
BYTES_PER_MIB = 1024 * 1024
OUTPUT_DIR = 'dataset'
HASH_BLOCK_SIZE = 32  # SHA-256 digest size in bytes

def sha256_counter_stream(seed: bytes, num_bytes: int):
    counter = 0
    produced = 0
    while produced < num_bytes:
        block = hashlib.sha256(seed + counter.to_bytes(8, 'big')).digest()
        take = min(HASH_BLOCK_SIZE, num_bytes - produced)
        yield block[:take]
        produced += take
        counter += 1

def generate_deterministic_file(path, size_mib, seed):
    size_bytes = size_mib * BYTES_PER_MIB
    with open(path, 'wb') as f:
        for chunk in sha256_counter_stream(seed, size_bytes):
            f.write(chunk)

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    checksums = []

    for name, mib in SIZES_MIB.items():
        path = os.path.join(OUTPUT_DIR, f'block_{name}.bin')
        generate_deterministic_file(path, mib, SEED)
        digest = sha256_of_file(path)
        checksums.append(f"{digest}  block_{name}.bin")
        print(f"Generated {path} -> {mib} MiB, SHA-256={digest}")

    with open(os.path.join(OUTPUT_DIR, 'SHA256SUMS.txt'), 'w') as f:
        f.write('\n'.join(checksums) + '\n')

    print("\nWritten SHA256SUMS.txt — every group should match these hashes exactly.")

