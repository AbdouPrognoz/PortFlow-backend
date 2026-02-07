from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.database import get_sync_db
from ....models.user import User, UserRole
from ....models.terminal import Terminal
from ....models.booking import Booking, BookingStatus
from ....models.notification import Notification, NotificationType
from ....schemas.booking import BookingResponse, BookingCreate, BookingUpdate, BookingConfirmationRequest
from ....schemas.terminal import TerminalResponse
from ....api.deps import get_current_user, require_role


router = APIRouter()


@router.get("/my-terminal", response_model=TerminalResponse)
async def get_my_terminal(
    current_user: User = Depends(require_role(["OPERATOR"])),
    db: Session = Depends(get_sync_db)
):
    # Get operator profile to find associated terminal
    operator_profile = current_user.operator_profile
    if not operator_profile or not operator_profile.terminal_id:
        raise HTTPException(status_code=404, detail="No terminal assigned to this operator")
    
    terminal = db.query(Terminal).filter(Terminal.id == operator_profile.terminal_id).first()
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    return terminal


@router.get("/bookings", response_model=list[BookingResponse])
async def get_terminal_bookings(
    status: BookingStatus = None,
    date: str = None,  # Expecting YYYY-MM-DD format
    current_user: User = Depends(require_role(["OPERATOR"])),
    db: Session = Depends(get_sync_db)
):
    # Get operator's terminal
    operator_profile = current_user.operator_profile
    if not operator_profile or not operator_profile.terminal_id:
        raise HTTPException(status_code=403, detail="Operator not assigned to a terminal")
    
    query = db.query(Booking).filter(Booking.terminal_id == operator_profile.terminal_id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    if date:
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(Booking.date == date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    bookings = query.all()
    return bookings


@router.post("/bookings/confirm", response_model=BookingResponse)
async def confirm_booking(
    confirmation_request: BookingConfirmationRequest,
    current_user: User = Depends(require_role(["OPERATOR"])),
    db: Session = Depends(get_sync_db)
):
    booking = db.query(Booking).filter(Booking.id == confirmation_request.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if the booking is for the operator's terminal
    operator_profile = current_user.operator_profile
    if not operator_profile or booking.terminal_id != operator_profile.terminal_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this booking")
    
    # Update booking status
    booking.status = confirmation_request.status
    booking.decided_by_operator_user_id = current_user.id
    
    # Generate QR payload if booking is confirmed
    if confirmation_request.status == BookingStatus.CONFIRMED:
        from ....utils.helpers import generate_qr_payload
        booking.qr_payload = generate_qr_payload(
            str(booking.id), 
            str(booking.terminal_id), 
            booking.updated_at or booking.created_at
        )
    
    db.commit()
    db.refresh(booking)
    
    # Create notification for the carrier
    notification = Notification(
        user_id=booking.carrier_user_id,
        type=NotificationType.BOOKING_CONFIRMED,
        message=f"Your booking for {booking.date} has been {confirmation_request.status.value}",
        related_booking_id=booking.id
    )
    db.add(notification)
    db.commit()
    
    return booking


@router.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_update: BookingUpdate,
    current_user: User = Depends(require_role(["OPERATOR"])),
    db: Session = Depends(get_sync_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if the booking is for the operator's terminal
    operator_profile = current_user.operator_profile
    if not operator_profile or booking.terminal_id != operator_profile.terminal_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this booking")
    
    # Update allowed fields
    if booking_update.status:
        booking.status = booking_update.status
    if booking_update.driver_user_id:
        booking.driver_user_id = booking_update.driver_user_id
    if booking_update.decided_by_operator_user_id:
        booking.decided_by_operator_user_id = booking_update.decided_by_operator_user_id
    
    db.commit()
    db.refresh(booking)
    
    return booking