import uuid
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional

from app.services.pdf_service import get_pdf_service
from app.services.firestore_service import get_firestore_service
from app.schemas.user_schemas import SavedItineraryDocument

logger = logging.getLogger(__name__)

class ItineraryService:
    def __init__(self):
        """Initialize itinerary service"""
        self.pdf_service = get_pdf_service()
        self.firestore_service = get_firestore_service()

    async def create_and_save_complete_itinerary(
        self,
        trip_summary: str,
        user_name: str,
        destination: str,
        start_date: date,
        end_date: date,
        flights: List[dict],
        hotels: List[dict],
        daily_plans: List[dict],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create PDF itinerary and save to user profile if authenticated"""
        try:
            # Create the PDF
            pdf_result = await self.pdf_service.create_and_save_itinerary_pdf(
                trip_summary, user_name, destination, start_date, end_date,
                flights, hotels, daily_plans
            )
            
            if not pdf_result.get('success'):
                return pdf_result
            
            # If user is authenticated, save to their profile
            if user_id:
                # Create itinerary document
                itinerary_doc = SavedItineraryDocument(
                    id=str(uuid.uuid4()),
                    title=f"{destination} - {start_date.strftime('%b %Y')}",
                    destination=destination,
                    start_date=start_date,
                    end_date=end_date,
                    pdf_url=pdf_result['pdf_url'],
                    created_at=pdf_result['created_at'],
                    file_size_mb=pdf_result['file_size_mb']
                )
                
                # Save to user profile
                saved = await self.firestore_service.save_user_itinerary(user_id, itinerary_doc)
                if saved:
                    pdf_result['saved_to_profile'] = True
                    pdf_result['message'] = f"✅ Your {destination} itinerary has been created and saved to your profile!"
                else:
                    pdf_result['saved_to_profile'] = False
                    pdf_result['message'] = f"✅ Your {destination} itinerary PDF has been created, but couldn't save to profile."
            else:
                pdf_result['saved_to_profile'] = False
                pdf_result['message'] = f"✅ Your {destination} itinerary PDF has been created! Sign up to save itineraries to your profile."
            
            return pdf_result
            
        except Exception as e:
            logger.error(f"Error creating complete itinerary: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "❌ Failed to create itinerary PDF. Please try again."
            }

    async def get_user_itineraries(self, user_id: str) -> List[SavedItineraryDocument]:
        """Get all saved itineraries for a user"""
        return await self.firestore_service.get_user_itineraries(user_id)

    async def delete_user_itinerary(self, user_id: str, itinerary_id: str) -> bool:
        """Delete a user's saved itinerary"""
        return await self.firestore_service.delete_user_itinerary(user_id, itinerary_id)


# Singleton instance
_itinerary_service = None

def get_itinerary_service() -> ItineraryService:
    """Dependency injection for ItineraryService"""
    global _itinerary_service
    if _itinerary_service is None:
        _itinerary_service = ItineraryService()
    return _itinerary_service 