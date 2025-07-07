from fastapi import APIRouter, HTTPException, status, Depends
from app.services.itinerary_service import get_itinerary_service
from app.middleware.auth_middleware import get_current_user_required
from app.schemas.auth_schemas import UserResponse
from app.schemas.user_schemas import SavedItineraryDocument
from typing import List
import logging

router = APIRouter(prefix="/itinerary", tags=["itinerary"])
logger = logging.getLogger(__name__)

@router.get("/saved", response_model=List[SavedItineraryDocument])
async def get_saved_itineraries(
    current_user: UserResponse = Depends(get_current_user_required)
):
    """
    Get all saved itineraries for the current user.
    
    Returns:
        List[SavedItineraryDocument]: List of user's saved itineraries
    """
    try:
        itinerary_service = get_itinerary_service()
        itineraries = await itinerary_service.get_user_itineraries(current_user.id)
        return itineraries
    except Exception as e:
        logger.error(f"Error getting saved itineraries for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve saved itineraries"
        )

@router.delete("/saved/{itinerary_id}")
async def delete_saved_itinerary(
    itinerary_id: str,
    current_user: UserResponse = Depends(get_current_user_required)
):
    """
    Delete a specific saved itinerary for the current user.
    
    Args:
        itinerary_id: ID of the itinerary to delete
        
    Returns:
        Success message
    """
    try:
        itinerary_service = get_itinerary_service()
        success = await itinerary_service.delete_user_itinerary(current_user.id, itinerary_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found or could not be deleted"
            )
        
        return {"message": "Itinerary deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting itinerary {itinerary_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete itinerary"
        )

@router.delete("/saved")
async def delete_all_saved_itineraries(
    current_user: UserResponse = Depends(get_current_user_required)
):
    """
    Delete all saved itineraries for the current user.
    
    Returns:
        Success message
    """
    try:
        itinerary_service = get_itinerary_service()
        
        # Get all itineraries first
        itineraries = await itinerary_service.get_user_itineraries(current_user.id)
        
        # Delete each one
        deleted_count = 0
        for itinerary in itineraries:
            success = await itinerary_service.delete_user_itinerary(current_user.id, itinerary.id)
            if success:
                deleted_count += 1
        
        return {"message": f"Deleted {deleted_count} itineraries successfully"}
    except Exception as e:
        logger.error(f"Error deleting all itineraries for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete all itineraries"
        ) 