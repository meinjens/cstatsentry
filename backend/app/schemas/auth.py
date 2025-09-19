from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SteamAuthResponse(BaseModel):
    steam_id: str
    steam_name: str
    avatar_url: Optional[str] = None
    access_token: str
    token_type: str = "bearer"


class SteamAuthCallback(BaseModel):
    """Schema for Steam OpenID callback parameters"""
    # These are the standard OpenID parameters we expect
    openid_mode: str
    openid_claimed_id: Optional[str] = None
    openid_identity: Optional[str] = None
    openid_return_to: Optional[str] = None
    openid_response_nonce: Optional[str] = None
    openid_assoc_handle: Optional[str] = None
    openid_signed: Optional[str] = None
    openid_sig: Optional[str] = None

    class Config:
        # Allow extra fields for any additional OpenID parameters
        extra = "allow"