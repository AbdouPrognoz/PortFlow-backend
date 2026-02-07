from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, date
from uuid import UUID
from ....core.database import get_sync_db
from ....core.security import verify_password, get_password_hash, create_access_token
from ....models.user import User, UserRole
from ....models.profile import OperatorProfile, CarrierProfile, DriverProfile, CarrierStatus, DriverStatus
from ....schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from ....schemas.user import UserCreate
from ....api.deps import get_current_user


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_sync_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Prepare user response with profile data
    profile_data = None
    if user.role == UserRole.OPERATOR:
        profile = db.query(OperatorProfile).filter(OperatorProfile.user_id == user.id).first()
        if profile:
            profile_data = {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "phone": profile.phone,
                "gender": profile.gender,
                "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
                "terminal_id": str(profile.terminal_id) if profile.terminal_id else None
            }
    elif user.role == UserRole.CARRIER:
        profile = db.query(CarrierProfile).filter(CarrierProfile.user_id == user.id).first()
        if profile:
            profile_data = {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "phone": profile.phone,
                "gender": profile.gender,
                "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
                "company_name": profile.company_name,
                "status": profile.status.value
            }
    elif user.role == UserRole.DRIVER:
        profile = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
        if profile:
            profile_data = {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "phone": profile.phone,
                "gender": profile.gender,
                "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
                "truck_number": profile.truck_number,
                "truck_plate": profile.truck_plate,
                "status": profile.status.value
            }
    
    user_response = {
        "id": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "profile": profile_data
    }
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_sync_db)
):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == register_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Parse birth_date if provided
    parsed_birth_date = None
    if register_data.birth_date:
        try:
            parsed_birth_date = date.fromisoformat(register_data.birth_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid birth_date format. Use YYYY-MM-DD"
            )
    
    try:
        # Hash the password
        hashed_password = get_password_hash(register_data.password)
        
        # Create the user
        user = User(
            email=register_data.email,
            password_hash=hashed_password,
            role=UserRole(register_data.role),
            is_active=True
        )
        
        db.add(user)
        db.flush()  # Get user.id without committing
        
        # Create profile based on role
        if user.role == UserRole.CARRIER:
            profile = CarrierProfile(
                user_id=user.id,
                first_name=register_data.first_name,
                last_name=register_data.last_name,
                phone=register_data.phone,
                gender=register_data.gender,
                birth_date=parsed_birth_date,
                company_name=register_data.company_name,
                status=CarrierStatus.PENDING
            )
            db.add(profile)
        elif user.role == UserRole.OPERATOR:
            profile = OperatorProfile(
                user_id=user.id,
                first_name=register_data.first_name,
                last_name=register_data.last_name,
                phone=register_data.phone,
                gender=register_data.gender,
                birth_date=parsed_birth_date
            )
            db.add(profile)
        elif user.role == UserRole.DRIVER:
            if not register_data.carrier_user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="carrier_user_id is required for driver registration"
                )
            try:
                carrier_uuid = UUID(register_data.carrier_user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid carrier_user_id format"
                )
            profile = DriverProfile(
                user_id=user.id,
                carrier_user_id=carrier_uuid,
                first_name=register_data.first_name,
                last_name=register_data.last_name,
                phone=register_data.phone,
                gender=register_data.gender,
                birth_date=parsed_birth_date,
                status=DriverStatus.ACTIVE
            )
            db.add(profile)
        
        db.commit()
        db.refresh(user)
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    user_response = {
        "id": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "profile": None
    }
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )