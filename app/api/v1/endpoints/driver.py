from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.database import get_sync_db
from ....models.user import User, UserRole
from ....models.booking import Booking, BookingStatus
from ....schemas.booking import BookingResponse
from ....api.deps import get_current_user, require_role


router = APIRouter()


@router.get("/my-bookings", response_model=list[BookingResponse])
async def get_my_assignments(
    status: BookingStatus = None,
    current_user: User = Depends(require_role(["DRIVER"])),
    db: Session = Depends(get_sync_db)
):
    query = db.query(Booking).filter(Booking.driver_user_id == str(current_user.id))
    
    if status:
        query = query.filter(Booking.status == status)
    
    bookings = query.all()
    return bookings


@router.get("/available-bookings", response_model=list[BookingResponse])
async def get_available_bookings(
    date: str = None,  # Expecting YYYY-MM-DD format
    current_user: User = Depends(require_role(["DRIVER"])),
    db: Session = Depends(get_sync_db)
):
    # Get the driver's carrier
    driver_profile = current_user.driver_profile
    if not driver_profile:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    # Find bookings that are assigned to the same carrier and are confirmed
    query = db.query(Booking).filter(
        Booking.carrier_user_id == driver_profile.carrier_user_id,
        Booking.status == BookingStatus.CONFIRMED,
        Booking.driver_user_id.is_(None)  # Not yet assigned to a driver
    )
    
    if date:
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(Booking.date == date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    bookings = query.all()
    return bookings


@router.post("/assign-to-booking/{booking_id}", response_model=BookingResponse)
async def assign_to_booking(
    booking_id: str,
    current_user: User = Depends(require_role(["DRIVER"])),
    db: Session = Depends(get_sync_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if the booking belongs to the same carrier as the driver
    driver_profile = current_user.driver_profile
    if not driver_profile or booking.carrier_user_id != driver_profile.carrier_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to assign to this booking")
    
    # Check if booking is confirmed and not already assigned
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Can only assign to confirmed bookings")
    
    if booking.driver_user_id:
        raise HTTPException(status_code=400, detail="Booking already assigned to a driver")
    
    # Assign the driver to the booking
    booking.driver_user_id = current_user.id
    db.commit()
    db.refresh(booking)
    
    return booking


@router.post("/consume-booking/{booking_id}", response_model=BookingResponse)
async def consume_booking(
    booking_id: str,
    current_user: User = Depends(require_role(["DRIVER"])),
    db: Session = Depends(get_sync_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if the booking is assigned to this driver
    if str(booking.driver_user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to consume this booking")
    
    # Check if booking is confirmed
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Can only consume confirmed bookings")
    
    # Update booking status to consumed
    booking.status = BookingStatus.CONSUMED
    db.commit()
    db.refresh(booking)
    
    return booking