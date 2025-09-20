from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import SteamAuthResponse, Token
from app.schemas.user import User as UserSchema
from app.services.steam_auth import steam_auth
from app.services.steam_api import steam_api, SteamDataExtractor
from app.crud.user import get_user_by_steam_id, create_user, update_user
from app.core.security import create_access_token
from app.api.deps import get_current_user
from datetime import timedelta
from app.core.config import settings

router = APIRouter()


@router.get("/steam/login")
async def steam_login():
    """Initiate Steam OAuth login"""
    auth_url = steam_auth.get_auth_url()
    return {"auth_url": auth_url}


@router.get("/steam/callback")
async def steam_callback(
    db: Session = Depends(get_db),
    # Steam OpenID parameters
    openid_mode: str = Query(..., alias="openid.mode"),
    openid_claimed_id: str = Query(None, alias="openid.claimed_id"),
    openid_identity: str = Query(None, alias="openid.identity"),
    openid_return_to: str = Query(None, alias="openid.return_to"),
    openid_response_nonce: str = Query(None, alias="openid.response_nonce"),
    openid_assoc_handle: str = Query(None, alias="openid.assoc_handle"),
    openid_signed: str = Query(None, alias="openid.signed"),
    openid_sig: str = Query(None, alias="openid.sig"),
) -> SteamAuthResponse:
    """Handle Steam OAuth callback"""

    # Collect all OpenID parameters
    openid_params = {
        "openid.mode": openid_mode,
    }

    if openid_claimed_id:
        openid_params["openid.claimed_id"] = openid_claimed_id
    if openid_identity:
        openid_params["openid.identity"] = openid_identity
    if openid_return_to:
        openid_params["openid.return_to"] = openid_return_to
    if openid_response_nonce:
        openid_params["openid.response_nonce"] = openid_response_nonce
    if openid_assoc_handle:
        openid_params["openid.assoc_handle"] = openid_assoc_handle
    if openid_signed:
        openid_params["openid.signed"] = openid_signed
    if openid_sig:
        openid_params["openid.sig"] = openid_sig

    # Verify Steam authentication
    steam_id = await steam_auth.verify_auth_response(openid_params)

    if not steam_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Steam authentication failed"
        )

    # Get user profile from Steam API
    try:
        async with steam_api:
            player_data = await steam_api.get_player_summaries([steam_id])

            if not player_data.get("response", {}).get("players"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not fetch Steam profile"
                )

            player_info = player_data["response"]["players"][0]
            extracted_data = SteamDataExtractor.extract_player_data(player_info)

    except HTTPException:
        raise  # Re-raise HTTPExceptions as is
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Steam API error: {str(e)}"
        )

    # Create or update user
    user = get_user_by_steam_id(db, steam_id)
    if user:
        # Update existing user
        update_data = {
            "steam_name": extracted_data["current_name"],
            "avatar_url": extracted_data["avatar_url"]
        }
        user = update_user(db, user, update_data)
    else:
        # Create new user
        user_data = {
            "steam_id": steam_id,
            "steam_name": extracted_data["current_name"],
            "avatar_url": extracted_data["avatar_url"]
        }
        user = create_user(db, user_data)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=steam_id, expires_delta=access_token_expires
    )

    return SteamAuthResponse(
        steam_id=steam_id,
        steam_name=user.steam_name or "",
        avatar_url=user.avatar_url,
        access_token=access_token
    )


@router.post("/refresh")
async def refresh_token(
    current_user: UserSchema = Depends(get_current_user)
) -> Token:
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.steam_id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


@router.get("/me")
async def get_current_user_info(
    current_user: UserSchema = Depends(get_current_user)
) -> UserSchema:
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}