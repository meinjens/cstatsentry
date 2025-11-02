"""
CS2/CSGO Match Sharecode Decoder

Based on: https://github.com/joshuaferrara/node-csgo/blob/master/helpers/sharecode.js
Reference: https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Access_Match_History

Sharecode format: CSGO-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx
Each group is a base-57 encoded value
"""

import struct
from typing import Optional, Dict, Any


# Dictionary for base-57 encoding/decoding
DICTIONARY = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefhijkmnopqrstuvwxyz23456789"
DICTIONARY_LEN = len(DICTIONARY)


def decode_sharecode(sharecode: str) -> Optional[Dict[str, Any]]:
    """
    Decode a CS2/CSGO match sharecode to match details

    Args:
        sharecode: Match sharecode in format CSGO-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx

    Returns:
        Dictionary with matchId, outcomeId, tokenId or None if invalid
    """
    try:
        # Remove CSGO- prefix and hyphens
        if sharecode.startswith("CSGO-"):
            sharecode = sharecode[5:]

        sharecode = sharecode.replace("-", "")

        if len(sharecode) != 25:
            return None

        # Decode from base-57 (TS implementation style)
        chars = list(reversed(sharecode))
        big_int = 0
        for char in chars:
            if char not in DICTIONARY:
                return None
            big_int = big_int * DICTIONARY_LEN + DICTIONARY.index(char)

        # Convert to hex string, pad to 36 hex chars (18 bytes)
        hex_str = format(big_int, 'x').zfill(36)

        # Convert hex string to bytes
        all_bytes = bytes.fromhex(hex_str)

        # Parse the structure (reverse slices like TS):
        # First 8 bytes (reversed): matchId (uint64)
        # Next 8 bytes (reversed): outcomeId/reservationId (uint64)
        # Last 2 bytes (reversed): tokenId/tvPort (uint16)

        match_id = int.from_bytes(bytes(reversed(all_bytes[0:8])), byteorder='big')
        outcome_id = int.from_bytes(bytes(reversed(all_bytes[8:16])), byteorder='big')
        token_id = int.from_bytes(bytes(reversed(all_bytes[16:18])), byteorder='big')

        return {
            "matchId": match_id,
            "outcomeId": outcome_id,
            "tokenId": token_id
        }

    except Exception as e:
        return None


def encode_sharecode(match_id: int, outcome_id: int, token_id: int) -> Optional[str]:
    """
    Encode match details to a sharecode

    Args:
        match_id: Match ID (uint64)
        outcome_id: Outcome ID (uint64)
        token_id: Token ID (uint16)

    Returns:
        Sharecode string or None if invalid
    """
    try:
        # Convert to hex and reverse bytes (TS style)
        match_hex = format(match_id, 'x').zfill(16)
        outcome_hex = format(outcome_id, 'x').zfill(16)
        token_hex = format(token_id, 'x').zfill(4)

        # Convert hex to bytes and reverse
        match_bytes = list(reversed(bytes.fromhex(match_hex)))
        outcome_bytes = list(reversed(bytes.fromhex(outcome_hex)))
        token_bytes = list(reversed(bytes.fromhex(token_hex)))

        # Combine all bytes
        all_bytes = match_bytes + outcome_bytes + token_bytes

        # Convert bytes to hex string
        hex_str = ''.join(format(b, '02x') for b in all_bytes)

        # Convert to BigInt
        big_int = int(hex_str, 16)

        # Encode to base-57 (TS style)
        chars = ''
        for _ in range(25):
            rem = big_int % DICTIONARY_LEN
            chars += DICTIONARY[rem]
            big_int //= DICTIONARY_LEN

        # Format with hyphens
        formatted = f"CSGO-{chars[0:5]}-{chars[5:10]}-{chars[10:15]}-{chars[15:20]}-{chars[20:25]}"

        return formatted

    except Exception as e:
        return None


def get_demo_url(match_id: int, outcome_id: int, token_id: int, replay_server: int = 124) -> str:
    """
    Construct demo download URL from match details

    Args:
        match_id: Match ID
        outcome_id: Outcome ID
        token_id: Token ID
        replay_server: Replay server number (default 124)

    Returns:
        Demo download URL
    """
    # Demo filename format: {matchId}_{outcomeId}.dem.bz2
    filename = f"{str(match_id).zfill(21)}_{str(outcome_id).zfill(10)}.dem.bz2"

    # URL format: http://replayXXX.valve.net/730/{filename}
    return f"http://replay{replay_server}.valve.net/730/{filename}"


def get_demo_url_from_sharecode(sharecode: str, replay_server: int = 124) -> Optional[str]:
    """
    Get demo URL directly from sharecode

    Args:
        sharecode: Match sharecode
        replay_server: Replay server number (default 124)

    Returns:
        Demo download URL or None if sharecode is invalid
    """
    decoded = decode_sharecode(sharecode)
    if not decoded:
        return None

    return get_demo_url(
        decoded['matchId'],
        decoded['outcomeId'],
        decoded['tokenId'],
        replay_server
    )


# Validation functions
def validate_sharecode(sharecode: str) -> bool:
    """Check if sharecode is valid format"""
    if not sharecode:
        return False

    # Remove prefix
    code = sharecode.replace("CSGO-", "").replace("-", "")

    # Check length
    if len(code) != 25:
        return False

    # Check all characters are in dictionary
    return all(c in DICTIONARY for c in code)


if __name__ == "__main__":
    # Test with example sharecode
    test_sharecode = "CSGO-U6MWi-5cZMJ-VsXtM-yrOwD-g8BJJ"

    print(f"Testing sharecode: {test_sharecode}")
    print(f"Valid: {validate_sharecode(test_sharecode)}")

    decoded = decode_sharecode(test_sharecode)
    if decoded:
        print(f"Decoded: {decoded}")
        print(f"Demo URL: {get_demo_url_from_sharecode(test_sharecode)}")

        # Test encoding back
        encoded = encode_sharecode(
            decoded['matchId'],
            decoded['outcomeId'],
            decoded['tokenId']
        )
        print(f"Re-encoded: {encoded}")
        print(f"Match: {encoded == test_sharecode}")
    else:
        print("Failed to decode")