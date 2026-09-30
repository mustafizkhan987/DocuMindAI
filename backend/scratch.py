CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def _calculate_checksum(gstin_14: str) -> str:
    total_sum = 0
    for i, char in enumerate(gstin_14):
        val = CHARS.find(char)
        factor = 1 if (i % 2 == 0) else 2
        product = val * factor
        quotient = product // 36
        remainder = product % 36
        total_sum += quotient + remainder
        
    checksum_val = (36 - (total_sum % 36)) % 36
    return CHARS[checksum_val]

print("06BZAHM6385P6Z:", _calculate_checksum("06BZAHM6385P6Z"))
