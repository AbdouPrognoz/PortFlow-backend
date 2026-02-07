from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.database import get_sync_db
from ....models.terminal import Terminal
from ....models.user import User
from ....models.profile import OperatorProfile
from ....schemas.terminal import TerminalResponse, TerminalListResponse
from ....schemas.user import UserResponse
from ....api.deps import get_current_user, require_role


router = APIRouter()


@router.get("/terminals", response_model=TerminalListResponse)
async def get_all_terminals(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    terminals = db.query(Terminal).offset(skip).limit(limit).all()
    terminal_responses = []
    
    for terminal in terminals:
        terminal_responses.append({
            "id": str(terminal.id),
            "name": terminal.name,
            "status": terminal.status.value,
            "max_slots": terminal.max_slots,
            "available_slots": terminal.available_slots,
            "coord_x": terminal.coord_x,
            "coord_y": terminal.coord_y,
            "created_at": terminal.created_at,
            "updated_at": terminal.updated_at
        })
    
    return TerminalListResponse(
        status="success",
        message="Terminals retrieved successfully",
        data=terminal_responses
    )


@router.get("/profile", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    profile_data = None
    
    if current_user.role == User.UserRole.OPERATOR:
        profile = db.query(OperatorProfile).filter(OperatorProfile.user_id == current_user.id).first()
        if profile:
            profile_data = {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "phone": profile.phone,
                "gender": profile.gender,
                "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
                "terminal_id": str(profile.terminal_id) if profile.terminal_id else None
            }
    elif current_user.role == User.UserRole.CARRIER:
        from ....models.profile import CarrierProfile
        profile = db.query(CarrierProfile).filter(CarrierProfile.user_id == current_user.id).first()
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
    elif current_user.role == User.UserRole.DRIVER:
        from ....models.profile import DriverProfile
        profile = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
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
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        profile=profile_data
    )