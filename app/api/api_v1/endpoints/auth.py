from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.auth import UserAuth, TokenData
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from app.core.supabase import supabase 

from app.api import deps

router = APIRouter()


################################################################################################
#  Sign up with email and password
################################################################################################
@router.post("/signup")
async def sign_up(user: UserAuth):
    try:
        response = supabase.auth.sign_up({
            'email': user.email,
            'password': user.password
        })
        if not response.user:
            raise HTTPException(status_code=400, detail="Sign-up failed")
        return {"message": "User signed up successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#################################################################################################
#   Log in with email and password
#################################################################################################
@router.post("/signin")
async def sign_in(user: UserAuth):
    try:
        response = supabase.auth.sign_in_with_password({
            'email': user.email,
            'password': user.password
        })
        if not response.user:
            raise HTTPException(status_code=400, detail="Sign-in failed")
        return {"message": "User signed in successfully", "session": response.session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#################################################################################################
#   OAuth with google
#################################################################################################
@router.post("/google")
async def auth_google():  
    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                # "redirect_to": "http://127.0.0.1:8000/api/v1/auth/callback"  
                "redirect_to" : "http://localhost:3000/oauth/callback/"
            }
        })
        # print(response.url)
        if response:
            return {"redirect_url": response.url}
        else:
            raise HTTPException(status_code=500, detail="OAuth sign-in failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth sign-in failed: {e}")

#################################################################################################
#   OAuth with facebook
#################################################################################################
@router.post("/facebook")
async def auth_facebook():  
    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": "facebook",
            "options": {
                "redirect_to": "http://127.0.0.1:8000/api/v1/auth/callback"  
            }
        })
        if response:
            return {"redirect_url": response.url}
        else:
            raise HTTPException(status_code=500, detail="OAuth sign-in failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth sign-in failed: {e}")

#################################################################################################
#   callback function
#################################################################################################
@router.get("/callback")
async def auth_callback(request: Request):
    full_url = str(request.url)
    html_content = f"""
    <html>
        <head>
            <script>
                const hash = window.location.hash.substr(1);
                const params = new URLSearchParams(hash);
                const access_token = params.get('access_token');
                if (access_token) {{
                    window.opener.postMessage({{ token: access_token }}, "*");
                }}
                window.close();
            </script>
        </head>
    </html>
    """
    return HTMLResponse(content=html_content)

#################################################################################################
#   Token exchange
#################################################################################################
@router.post("/exchange-token")
async def exchange_token(token_data: TokenData):
    try:
        user = supabase.auth.get_user(token_data.token)
        if user:
            return {
                "message": "Token exchanged successfully",
                "user_id": user.user.id,
                "email": user.user.email,
                "role": user.user.role
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#################################################################################################
#   Logout
#################################################################################################
@router.post("/logout")
async def log_out(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        supabase.auth.sign_out()
        return {"message": f"Logged Out"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
