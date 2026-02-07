from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.database import get_sync_db
from ....models.user import User, UserRole
from ....models.profile import CarrierProfile, DriverProfile
from ....schemas.user import UserResponse, UserListResponse, UserUpdate
from ....schemas.carrier import CarrierListResponse, CarrierApprovalRequest
from ....api.deps import get_current_user, require_role


router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    user_responses = []
    
    for user in users:
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
        
        user_responses.append({
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "profile": profile_data
        })
    
    return UserListResponse(
        status="success",
        message="Users retrieved successfully",
        data=user_responses
    )


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.get("/carriers", response_model=CarrierListResponse)
async def get_all_carriers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(["ADMIN", "OPERATOR"])),
    db: Session = Depends(get_sync_db)
):
    carriers = db.query(User).filter(User.role == UserRole.CARRIER).offset(skip).limit(limit).all()
    carrier_responses = []
    
    for user in carriers:
        profile = db.query(CarrierProfile).filter(CarrierProfile.user_id == user.id).first()
        if profile:
            carrier_responses.append({
                "user_id": str(user.id),
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "phone": profile.phone,
                "gender": profile.gender,
                "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
                "company_name": profile.company_name,
                "status": profile.status.value,
                "proof_document_url": profile.proof_document_url,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at
            })
    
    return CarrierListResponse(
        status="success",
        message="Carriers retrieved successfully",
        data=carrier_responses
    )


@router.post("/carriers/approve", response_model=dict)
async def approve_carrier(
    approval_request: CarrierApprovalRequest,
    current_user: User = Depends(require_role(["ADMIN", "OPERATOR"])),
    db: Session = Depends(get_sync_db)
):
    carrier_user = db.query(User).filter(User.id == approval_request.carrier_user_id).first()
    if not carrier_user or carrier_user.role != UserRole.CARRIER:
        raise HTTPException(status_code=404, detail="Carrier user not found")
    
    profile = db.query(CarrierProfile).filter(CarrierProfile.user_id == approval_request.carrier_user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Carrier profile not found")
    
    profile.status = approval_request.status
    db.commit()
    
    return {
        "status": "success",
        "message": f"Carrier status updated to {approval_request.status.value}"
    }