import re
from typing import Optional
from app.schemas.validation import GSTINValidationResult

class GSTINValidationService:
    CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def validate(self, gstin: Optional[str]) -> GSTINValidationResult:
        result = GSTINValidationResult(gstin=gstin)
        
        if not gstin or not str(gstin).strip():
            result.errors.append("MISSING_GSTIN")
            return result
            
        # Normalization
        normalized = str(gstin).strip().upper()
        result.normalized_gstin = normalized
        
        if len(normalized) != 15:
            result.errors.append("INVALID_LENGTH")
            return result
            
        if not re.match(r'^[0-9A-Z]+$', normalized):
            result.errors.append("INVALID_CHARACTERS")
            return result

        # Structure validation
        # 1. State Code (first 2 chars)
        state_code = normalized[0:2]
        # State codes are typically 01 to 38, and 97 to 99
        if not state_code.isdigit() or not (1 <= int(state_code) <= 38 or 97 <= int(state_code) <= 99):
            result.errors.append("INVALID_STATE_CODE")
            
        # 2. PAN Structure (next 10 chars)
        pan = normalized[2:12]
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan):
            result.errors.append("INVALID_PAN_STRUCTURE")
            
        # 3. Entity Number (13th char)
        entity_num = normalized[12]
        if not re.match(r'^[1-9A-Z]$', entity_num):
            result.errors.append("INVALID_ENTITY_NUMBER")
            
        # 4. Z character (14th char)
        z_char = normalized[13]
        if z_char != 'Z':
            result.errors.append("INVALID_FIXED_CHARACTER")
            
        result.format_valid = len(result.errors) == 0
        
        # 5. Checksum validation
        expected_checksum = self._calculate_checksum(normalized[:14])
        if expected_checksum:
            if normalized[14] != expected_checksum:
                result.errors.append("INVALID_CHECKSUM")
            else:
                result.checksum_valid = True
                
        result.is_valid = len(result.errors) == 0
        return result

    def _calculate_checksum(self, gstin_14: str) -> Optional[str]:
        if len(gstin_14) != 14:
            return None
            
        total_sum = 0
        for i, char in enumerate(gstin_14):
            val = self.CHARS.find(char)
            if val == -1:
                return None # Invalid character
                
            factor = 1 if i % 2 == 0 else 2
            product = val * factor
            quotient = product // 36
            remainder = product % 36
            total_sum += quotient + remainder
            
        checksum_val = (36 - (total_sum % 36)) % 36
        return self.CHARS[checksum_val]

gstin_validation_service = GSTINValidationService()
