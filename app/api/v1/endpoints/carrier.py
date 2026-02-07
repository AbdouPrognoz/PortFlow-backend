from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from ....core.database import get_sync_db
from ....models.user import User, UserRole
from ....models.booking import Booking, BookingStatus
from ....models.profile import DriverProfile
from ....schemas.booking import BookingResponse, BookingCreate
from ....schemas.driver import DriverProfileResponse
from ....api.deps import get_current_user, require_role


router = APIRouter()


@router.get("/my-bookings", response_model=list[BookingResponse])
async def get_my_bookings(
    status: BookingStatus = None,
    date: str = None,  # Expecting YYYY-MM-DD format
    current_user: User = Depends(require_role(["CARRIER"])),
    db: Session = Depends(get_sync_db)
):
    query = db.query(Booking).filter(Booking.carrier_user_id == current_user.id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(Booking.date == date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    bookings = query.all()
    return bookings


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(
    booking_create: BookingCreate,
    current_user: User = Depends(require_role(["CARRIER"])),
    db: Session = Depends(get_sync_db)
):
    # Verify that the carrier is creating a booking for themselves
    if booking_create.carrier_user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Cannot create booking for another carrier")
    
    # Check if the carrier is approved
    carrier_profile = current_user.carrier_profile
    if not carrier_profile or carrier_profile.status.value != "APPROVED":
        raise HTTPException(status_code=403, detail="Carrier not approved to create bookings")
    
    # Check for time conflicts
    conflicting_bookings = db.query(Booking).filter(
        Booking.terminal_id == booking_create.terminal_id,
        Booking.date == booking_create.date,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        ((Booking.start_time < booking_create.end_time) & (Booking.end_time > booking_create.start_time))
    ).all()
    
    if conflicting_bookings:
        raise HTTPException(status_code=409, detail="Time slot already booked at this terminal")
    
    # Create the booking
    booking = Booking(
        carrier_user_id=booking_create.carrier_user_id,
        terminal_id=booking_create.terminal_id,
        date=booking_create.date,
        start_time=booking_create.start_time,
        end_time=booking_create.end_time,
        status=BookingStatus.PENDING
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return booking


@router.get("/drivers", response_model=list[DriverProfileResponse])
async def get_my_drivers(
    current_user: User = Depends(require_role(["CARRIER"])),
    db: Session = Depends(get_sync_db)
):
    # Get all drivers associated with this carrier
    drivers = db.query(DriverProfile).filter(
        DriverProfile.carrier_user_id == current_user.id
    ).all()
    
    return drivers


@router.delete("/bookings/{booking_id}", response_model=dict)
async def cancel_booking(
    booking_id: str,
    current_user: User = Depends(require_role(["CARRIER"])),
    db: Session = Depends(get_sync_db)
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.carrier_user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not owned by carrier")
    
    # Cannot cancel if already processed
    if booking.status in [BookingStatus.CONFIRMED, BookingStatus.REJECTED, BookingStatus.CONSUMED]:
        raise HTTPException(status_code=400, detail="Cannot cancel booking in current status")
    
    booking.status = BookingStatus.CANCELLED
    db.commit()
    
    return {"status": "success", "message": "Booking cancelled successfully"}