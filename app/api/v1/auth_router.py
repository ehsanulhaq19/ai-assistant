from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repository import UserRepository
from app.core.auth import verify_password, get_password_hash, create_access_token
from app.schemas.user import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, LogoutResponse, PlanUpdateRequest, PlanUpdateResponse
from app.models.user import User, PlanType
from app.utils import generate_session_id
from app.core.auth_dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, summary="Register a new user", description="Create a new user account. No authentication required.")
def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    if user_repo.get_by_email(request.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        name=request.name,
        hashed_password=hashed_password,
        plan_type=request.plan_type
    )
    user_repo.create(user)
    return user

@router.post("/login", response_model=TokenResponse, summary="Login user", description="Authenticate user and return JWT token. No authentication required.")
def login_user(request: UserLoginRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_id = generate_session_id()
    user_repo.set_session_id(user.id, session_id)
    
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, session_id=session_id, user_id=user.id)

@router.post("/logout", response_model=LogoutResponse, summary="Logout user", description="Logout user and invalidate session. Authentication required.")
def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_repo.set_session_id(current_user.id, None)
    return LogoutResponse(message="Successfully logged out")

@router.put("/update-plan", response_model=PlanUpdateResponse, summary="Update user plan", description="Update user plan to pro or expert. Authentication required.")
def update_user_plan(
    request: PlanUpdateRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Validate that only pro or expert plans are allowed
    if request.plan_type not in [PlanType.PRO, PlanType.EXPERT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan type must be either 'pro' or 'expert'"
        )
    
    user_repo = UserRepository(db)
    success = user_repo.update_plan_type(current_user.id, request.plan_type)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return PlanUpdateResponse(
        message=f"Plan successfully updated to {request.plan_type.value}",
        user_id=current_user.id,
        new_plan_type=request.plan_type
    )
