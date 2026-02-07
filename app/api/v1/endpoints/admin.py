from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_sync_db
from ....models.user import User, UserRole
from ....models.terminal import Terminal, TerminalStatus
from ....models.booking import Booking, BookingStatus
from ....models.profile import OperatorProfile, CarrierProfile, DriverProfile
from ....models.notification import Notification, NotificationType
from ....schemas.user import UserResponse, UserListResponse, UserUpdate
from ....schemas.terminal import TerminalResponse, TerminalCreate, TerminalUpdate, TerminalListResponse
from ....schemas.booking import BookingResponse, BookingListResponse
from ....schemas.carrier import CarrierListResponse, CarrierApprovalRequest
from ....schemas.operator import OperatorProfileResponse
from ....schemas.driver import DriverProfileResponse
from ....api.deps import get_current_user, require_role


router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
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
                    "status": profile.status.value,
                    "carrier_user_id": str(profile.carrier_user_id)
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


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
                "status": profile.status.value,
                "carrier_user_id": str(profile.carrier_user_id)
            }
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile=profile_data
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
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(User.email == user_update.email).filter(User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered by another user")
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


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Actually delete the user (this will trigger CASCADE deletion for related records)
    db.delete(user)
    db.commit()
    
    return {
        "status": "success",
        "message": "User deleted successfully"
    }


@router.get("/terminals", response_model=TerminalListResponse)
async def get_all_terminals(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TerminalStatus] = None,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    query = db.query(Terminal)
    
    if status:
        query = query.filter(Terminal.status == status)
    
    terminals = query.offset(skip).limit(limit).all()
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


@router.post("/terminals", response_model=TerminalResponse)
async def create_terminal(
    terminal_create: TerminalCreate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    terminal = Terminal(
        name=terminal_create.name,
        status=TerminalStatus.ACTIVE,  # Default to active
        max_slots=terminal_create.max_slots,
        available_slots=terminal_create.available_slots,
        coord_x=terminal_create.coord_x,
        coord_y=terminal_create.coord_y
    )
    
    db.add(terminal)
    db.commit()
    db.refresh(terminal)
    
    return TerminalResponse(
        id=str(terminal.id),
        name=terminal.name,
        status=terminal.status.value,
        max_slots=terminal.max_slots,
        available_slots=terminal.available_slots,
        coord_x=terminal.coord_x,
        coord_y=terminal.coord_y,
        created_at=terminal.created_at,
        updated_at=terminal.updated_at
    )


@router.put("/terminals/{terminal_id}", response_model=TerminalResponse)
async def update_terminal(
    terminal_id: str,
    terminal_update: TerminalUpdate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    terminal = db.query(Terminal).filter(Terminal.id == terminal_id).first()
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    if terminal_update.name is not None:
        terminal.name = terminal_update.name
    if terminal_update.status is not None:
        terminal.status = terminal_update.status
    if terminal_update.max_slots is not None:
        terminal.max_slots = terminal_update.max_slots
    if terminal_update.available_slots is not None:
        terminal.available_slots = terminal_update.available_slots
    if terminal_update.coord_x is not None:
        terminal.coord_x = terminal_update.coord_x
    if terminal_update.coord_y is not None:
        terminal.coord_y = terminal_update.coord_y
    
    db.commit()
    db.refresh(terminal)
    
    return TerminalResponse(
        id=str(terminal.id),
        name=terminal.name,
        status=terminal.status.value,
        max_slots=terminal.max_slots,
        available_slots=terminal.available_slots,
        coord_x=terminal.coord_x,
        coord_y=terminal.coord_y,
        created_at=terminal.created_at,
        updated_at=terminal.updated_at
    )


@router.get("/carriers", response_model=CarrierListResponse)
async def get_all_carriers(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(require_role(["ADMIN", "OPERATOR"])),
    db: Session = Depends(get_sync_db)
):
    # Query users with carrier role
    user_query = db.query(User).filter(User.role == UserRole.CARRIER)
    
    # Apply status filter if provided
    if status:
        user_ids_with_status = db.query(CarrierProfile.user_id).filter(CarrierProfile.status.value == status).subquery()
        user_query = user_query.filter(User.id.in_(user_ids_with_status))
    
    users = user_query.offset(skip).limit(limit).all()
    carrier_responses = []
    
    for user in users:
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
    
    # Send notification to carrier about status change
    notification = Notification(
        user_id=approval_request.carrier_user_id,
        type=NotificationType.GENERIC,
        message=f"Your carrier account status has been updated to {approval_request.status.value}",
        related_booking_id=None
    )
    db.add(notification)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Carrier status updated to {approval_request.status.value}"
    }


@router.get("/bookings", response_model=BookingListResponse)
async def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[BookingStatus] = None,
    date: Optional[str] = None,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    query = db.query(Booking)
    
    if status:
        query = query.filter(Booking.status == status)
    
    if date:
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(Booking.date == date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    bookings = query.offset(skip).limit(limit).all()
    booking_responses = []
    
    for booking in bookings:
        booking_responses.append({
            "id": str(booking.id),
            "carrier_user_id": str(booking.carrier_user_id),
            "driver_user_id": str(booking.driver_user_id) if booking.driver_user_id else None,
            "terminal_id": str(booking.terminal_id),
            "date": booking.date,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "status": booking.status.value,
            "decided_by_operator_user_id": str(booking.decided_by_operator_user_id) if booking.decided_by_operator_user_id else None,
            "qr_payload": booking.qr_payload,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        })
    
    return BookingListResponse(
        status="success",
        message="Bookings retrieved successfully",
        data=booking_responses
    )