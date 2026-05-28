"""
Comprehensive UTF-8 repair for files with broken multi-byte sequences.

The previous encoding fix replaced bytes like 0x93, 0x94, 0x97, etc. with HTML
entities, but these bytes also appear as continuation bytes inside valid 4-byte
UTF-8 sequences (emoji, etc.) and 3-byte sequences.

This script does a byte-level walk through each file and reconstructs broken
multi-byte UTF-8 sequences by reversing the entity substitution.
"""

import glob
import re

# Maps: HTML entity string -> original byte value
ENTITY_TO_BYTE = {
    b'&mdash;': 0x97,
    b'&ndash;': 0x96,
    b'&ldquo;': 0x93,
    b'&rdquo;': 0x94,
    b'&lsquo;': 0x91,
    b'&rsquo;': 0x92,
    b'&hellip;': 0x85,
    b'&bull;': 0x95,
}

# Reverse: entity text lengths
ENTITY_LENGTHS = {k: len(k) for k in ENTITY_TO_BYTE}


def repair_file(raw: bytes) -> bytes:
    """Repair broken multi-byte UTF-8 sequences caused by naive byte replacement."""
    result = bytearray()
    i = 0
    n = len(raw)
    
    while i < n:
        b = raw[i]
        
        # Check if this is a UTF-8 multi-byte start byte
        if 0xC2 <= b <= 0xDF:  # 2-byte sequence start
            if i + 1 < n:
                b1 = raw[i + 1]
                if 0x80 <= b1 <= 0xBF:
                    # Valid 2-byte sequence
                    result.extend(raw[i:i+2])
                    i += 2
                else:
                    # Check if b1 is start of an entity we replaced
                    entity_found = False
                    for entity, orig_byte in ENTITY_TO_BYTE.items():
                        if raw[i+1:i+1+len(entity)] == entity:
                            # The original 3rd byte was orig_byte
                            # Reconstruct the 2-byte sequence
                            seq = bytes([b, orig_byte])
                            try:
                                char = seq.decode('utf-8')
                                result.extend(seq)
                            except:
                                # Fallback: output as HTML entities
                                result.extend(seq)
                            i += 1 + len(entity)
                            entity_found = True
                            break
                    if not entity_found:
                        result.append(b)
                        i += 1
            else:
                result.append(b)
                i += 1
                
        elif 0xE0 <= b <= 0xEF:  # 3-byte sequence start
            if i + 2 < n:
                b1 = raw[i + 1]
                if 0x80 <= b1 <= 0xBF:
                    b2 = raw[i + 2]
                    if 0x80 <= b2 <= 0xBF:
                        # Valid 3-byte sequence
                        result.extend(raw[i:i+3])
                        i += 3
                    else:
                        # b2 is not a valid continuation byte
                        # Check if b2 is start of an entity we replaced
                        entity_found = False
                        for entity, orig_byte in ENTITY_TO_BYTE.items():
                            if raw[i+2:i+2+len(entity)] == entity:
                                # The original 3rd byte was orig_byte
                                seq = bytes([b, b1, orig_byte])
                                try:
                                    char = seq.decode('utf-8')
                                    # Output as HTML entity for this character
                                    result.extend(f'&#{ord(char)};'.encode())
                                except:
                                    result.extend(seq)
                                i += 2 + len(entity)
                                entity_found = True
                                break
                        if not entity_found:
                            # b1 valid, b2 invalid but not entity - output b and b1
                            result.extend(raw[i:i+2])
                            i += 2
                elif 0x26 == b1 or (i+1 < n and raw[i+1:i+2] == b'&'):
                    # b1 is '&' - check if it's an entity we placed
                    entity_found = False
                    for entity, orig_byte in ENTITY_TO_BYTE.items():
                        if raw[i+1:i+1+len(entity)] == entity:
                            # Only b1 was replaced (unusual - b1 should be 0x80-0xBF)
                            # This means b itself might not be a 3-byte start
                            result.append(b)
                            i += 1
                            entity_found = True
                            break
                    if not entity_found:
                        result.append(b)
                        i += 1
                else:
                    result.append(b)
                    i += 1
            else:
                result.append(b)
                i += 1
                
        elif 0xF0 <= b <= 0xF4:  # 4-byte sequence start
            if i + 3 < n:
                b1, b2, b3 = raw[i+1], raw[i+2], raw[i+3]
                if (0x80 <= b1 <= 0xBF and 0x80 <= b2 <= 0xBF and 0x80 <= b3 <= 0xBF):
                    # Valid 4-byte sequence
                    result.extend(raw[i:i+4])
                    i += 4
                elif 0x80 <= b1 <= 0xBF:
                    # b1 is valid, check if b2 was replaced
                    entity_found = False
                    for entity, orig_byte in ENTITY_TO_BYTE.items():
                        if raw[i+2:i+2+len(entity)] == entity:
                            # The original 3rd byte was orig_byte
                            # The 4th byte should follow the entity
                            pos_after_entity = i + 2 + len(entity)
                            if pos_after_entity < n:
                                b3_orig = raw[pos_after_entity]
                                if 0x80 <= b3_orig <= 0xBF:
                                    seq = bytes([b, b1, orig_byte, b3_orig])
                                    try:
                                        char = seq.decode('utf-8')
                                        result.extend(f'&#{ord(char)};'.encode())
                                    except:
                                        result.extend(seq)
                                    i = pos_after_entity + 1
                                else:
                                    # 4th byte also invalid
                                    seq = bytes([b, b1, orig_byte])
                                    result.extend(seq)
                                    i = pos_after_entity
                            else:
                                seq = bytes([b, b1, orig_byte])
                                result.extend(seq)
                                i = pos_after_entity
                            entity_found = True
                            break
                    if not entity_found:
                        result.append(b)
                        i += 1
                else:
                    result.append(b)
                    i += 1
            else:
                result.append(b)
                i += 1
        else:
            result.append(b)
            i += 1
    
    return bytes(result)


all_files = (
    glob.glob('*.html') + 
    glob.glob('Services/*.html') + 
    glob.glob('PolicyPages/*.html')
)

fixed = []
for filepath in all_files:
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    # Strip BOM for processing (we'll add it back if it was there)
    has_bom = raw.startswith(b'\xef\xbb\xbf')
    if has_bom:
        raw_body = raw[3:]
    else:
        raw_body = raw
    
    repaired = repair_file(raw_body)
    
    if has_bom:
        repaired = b'\xef\xbb\xbf' + repaired
    
    if repaired != raw:
        with open(filepath, 'wb') as f:
            f.write(repaired)
        fixed.append(filepath)
        print(f'Fixed: {filepath}')

print(f'\nRepaired {len(fixed)} files.')

# Verify
print('\nVerifying UTF-8 validity:')
errors = []
for filepath in all_files:
    with open(filepath, 'rb') as f:
        raw = f.read()
    # Strip BOM
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError as e:
        errors.append((filepath, str(e)))
        print(f'  STILL BROKEN: {filepath}: {e}')

if not errors:
    print('  All files are valid UTF-8!')
else:
    print(f'  {len(errors)} files still have issues.')
