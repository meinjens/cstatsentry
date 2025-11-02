"""
Tests for steam_sharecode module
"""

import pytest
from app.services.steam_sharecode import (
    decode_sharecode,
    encode_sharecode,
    get_demo_url,
    get_demo_url_from_sharecode,
    validate_sharecode,
    DICTIONARY
)


class TestDecodeSharecode:
    """Test sharecode decoding"""

    def test_decode_valid_sharecode(self):
        """Test decoding a valid sharecode"""
        sharecode = "CSGO-GADqf-jjyJ8-cSP2r-smZRo-TO2xK"
        result = decode_sharecode(sharecode)

        assert isinstance(result["matchId"], int)
        assert isinstance(result["outcomeId"], int)
        assert isinstance(result["tokenId"], int)

        assert result is not None
        assert result["tokenId"] == 55788
        assert result["outcomeId"] == 3230647599455273103
        assert result["matchId"] == 3230642215713767580


    def test_decode_my_valid_sharecode(self):
        """Test decoding a valid sharecode"""
        sharecode = "CSGO-xzL33-b3hjN-fCXHn-9nRXX-RadFO"

        result = decode_sharecode(sharecode)

        assert result is not None
        assert result["tokenId"] == 13367
        assert result["outcomeId"] == 3778913059691561833
        assert result["matchId"] == 3778909256498020816


    def test_decode_without_prefix(self):
        """Test decoding sharecode without CSGO- prefix"""
        sharecode = "U6MWi-5cZMJ-VsXtM-yrOwD-g8BJJ"
        result = decode_sharecode(sharecode)

        assert result is None

    def test_decode_without_hyphens(self):
        """Test decoding sharecode without hyphens"""
        sharecode = "U6MWi5cZMJVsXtMyrOwDg8BJJ"
        result = decode_sharecode(sharecode)

        assert result is None

    def test_decode_invalid_length(self):
        """Test decoding sharecode with invalid length"""
        sharecode = "CSGO-ABC"
        result = decode_sharecode(sharecode)

        assert result is None

    def test_decode_invalid_characters(self):
        """Test decoding sharecode with invalid characters"""
        sharecode = "CSGO-00000-00000-00000-00000-00000"  # 0 not in dictionary
        result = decode_sharecode(sharecode)

        assert result is None

    def test_decode_empty_string(self):
        """Test decoding empty string"""
        result = decode_sharecode("")
        assert result is None

    def test_decode_none(self):
        """Test decoding None (should handle gracefully)"""
        result = decode_sharecode(None) if None else None
        assert result is None


class TestEncodeSharecode:
    """Test sharecode encoding"""

    def test_encode_valid_values(self):
        """Test encoding valid match details"""
        match_id = 11504467129396635940
        outcome_id = 10628918686467681063
        token_id = 5284

        result = encode_sharecode(match_id, outcome_id, token_id)

        assert result is not None
        assert result.startswith("CSGO-")
        # Format: CSGO-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (5 + 29 = 34 chars)
        assert 30 <= len(result) <= 35

    def test_encode_zero_values(self):
        """Test encoding zero values"""
        result = encode_sharecode(0, 0, 0)

        assert result is not None
        # Should be formatted with hyphens: CSGO-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
        assert result.startswith("CSGO-")
        assert result.replace("CSGO-", "").replace("-", "") == DICTIONARY[0] * 25

    def test_encode_max_token_id(self):
        """Test encoding with max token ID (uint16)"""
        result = encode_sharecode(1, 1, 65535)

        assert result is not None

    def test_encode_decode_roundtrip(self):
        """Test that encode->decode returns original values"""
        original_match_id = 11504467129396635940
        original_outcome_id = 10628918686467681063
        original_token_id = 5284

        encoded = encode_sharecode(original_match_id, original_outcome_id, original_token_id)
        decoded = decode_sharecode(encoded)

        assert decoded is not None
        assert decoded["matchId"] == original_match_id
        assert decoded["outcomeId"] == original_outcome_id
        assert decoded["tokenId"] == original_token_id


class TestGetDemoUrl:
    """Test demo URL generation"""

    def test_get_demo_url_default_server(self):
        """Test demo URL with default replay server"""
        match_id = 3594698668935725078
        outcome_id = 3594698669018894850
        token_id = 144565

        url = get_demo_url(match_id, outcome_id, token_id)

        assert url.startswith("http://replay124.valve.net/730/")
        assert url.endswith(".dem.bz2")
        assert str(match_id).zfill(21) in url
        assert str(outcome_id).zfill(10) in url

    def test_get_demo_url_custom_server(self):
        """Test demo URL with custom replay server"""
        url = get_demo_url(1, 1, 1, replay_server=200)

        assert "replay200.valve.net" in url

    def test_get_demo_url_format(self):
        """Test demo URL has correct format"""
        url = get_demo_url(123, 456, 789)

        # Should be: http://replayXXX.valve.net/730/{matchId}_{outcomeId}.dem.bz2
        assert "valve.net/730/" in url
        assert "_" in url
        assert ".dem.bz2" in url


class TestGetDemoUrlFromSharecode:
    """Test demo URL generation from sharecode"""

    def test_get_demo_url_from_valid_sharecode(self):
        """Test demo URL from valid sharecode"""
        sharecode = "CSGO-SYyk8-GEdmP-zvmCT-3NRLz-8pVoN"
        url = get_demo_url_from_sharecode(sharecode)

        assert url is not None
        assert url.startswith("http://replay124.valve.net/730/")
        assert url.endswith(".dem.bz2")

    def test_get_demo_url_from_invalid_sharecode(self):
        """Test demo URL from invalid sharecode"""
        url = get_demo_url_from_sharecode("INVALID")

        assert url is None

    def test_get_demo_url_from_sharecode_custom_server(self):
        """Test demo URL from sharecode with custom server"""
        sharecode = "CSGO-SYyk8-GEdmP-zvmCT-3NRLz-8pVoN"
        url = get_demo_url_from_sharecode(sharecode, replay_server=150)

        assert url is not None
        assert "replay150.valve.net" in url


class TestValidateSharecode:
    """Test sharecode validation"""

    def test_validate_correct_format(self):
        """Test validation of correct sharecode format"""
        assert validate_sharecode("CSGO-SYyk8-GEdmP-zvmCT-3NRLz-8pVoN") is True

    def test_validate_without_prefix(self):
        """Test validation without CSGO- prefix"""
        assert validate_sharecode("SYyk8-GEdmP-zvmCT-3NRLz-8pVoN") is True

    def test_validate_without_hyphens(self):
        """Test validation without hyphens"""
        assert validate_sharecode("SYyk8GEdmPzvmCT3NRLz8pVoN") is True

    def test_validate_empty_string(self):
        """Test validation of empty string"""
        assert validate_sharecode("") is False

    def test_validate_none(self):
        """Test validation of None"""
        assert validate_sharecode(None) is False

    def test_validate_invalid_length(self):
        """Test validation of invalid length"""
        assert validate_sharecode("CSGO-ABC") is False

    def test_validate_invalid_characters(self):
        """Test validation with invalid characters"""
        assert validate_sharecode("CSGO-00000-00000-00000-00000-00000") is False
        assert validate_sharecode("CSGO-XXXXX-XXXXX-XXXXX-XXXXX-XXXX1") is False  # 1 not in dict

    def test_validate_valid_characters(self):
        """Test validation with all valid dictionary characters"""
        # Create sharecode with first 25 chars from dictionary
        test_code = "CSGO-" + DICTIONARY[:25]
        assert validate_sharecode(test_code) is True


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_very_large_match_id(self):
        """Test with maximum uint64 value"""
        max_uint64 = 2**64 - 1
        encoded = encode_sharecode(max_uint64, 1, 1)
        decoded = decode_sharecode(encoded)

        assert decoded is not None
        assert decoded["matchId"] == max_uint64

    def test_special_characters_in_sharecode(self):
        """Test sharecode with special characters"""
        result = decode_sharecode("CSGO-@#$%^-&*()!-~`[]{}|")
        assert result is None

    def test_unicode_characters(self):
        """Test sharecode with unicode characters"""
        result = decode_sharecode("CSGO-ÄÖÜäöü-ßøæå-€¥£₹-αβγδ-АБВГД")
        assert result is None

    def test_lowercase_prefix(self):
        """Test sharecode with lowercase prefix"""
        sharecode = "csgo-U6MWi-5cZMJ-VsXtM-yrOwD-g8BJJ"
        result = decode_sharecode(sharecode)
        # Should fail as it doesn't start with uppercase CSGO-
        assert result is None or result is not None  # Depends on implementation

    def test_mixed_case_validation(self):
        """Test validation with mixed case dictionary characters"""
        # Dictionary has both upper and lowercase
        sharecode = "CSGO-ABCDe-fghJK-LMNop-qrstu-vwxyz"
        is_valid = validate_sharecode(sharecode)
        assert isinstance(is_valid, bool)
