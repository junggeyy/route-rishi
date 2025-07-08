import io
import uuid
from datetime import datetime, date
from datetime import timedelta
from typing import List, Dict, Any, Optional
import logging

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, blue, darkgreen
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors

import firebase_admin
from firebase_admin import storage
from app.core.config import settings

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        """Initialize PDF service with Firebase Storage"""
        try:
            # Ensure Firebase is initialized by importing and instantiating FirebaseService
            if not firebase_admin._apps:
                logger.info("Firebase not initialized, initializing via FirebaseService...")
                from app.services.firebase_service import FirebaseService
                FirebaseService()  
            
            self.bucket = storage.bucket(settings.FIREBASE_STORAGE_BUCKET)
        except Exception as e:
            logger.error(f"Failed to initialize PDF service: {e}")
            raise

    def create_itinerary_pdf(
        self,
        trip_summary: str,
        user_name: str,
        destination: str,
        start_date: date,
        end_date: date,
        flights: List[Dict[str, Any]],
        hotels: List[Dict[str, Any]],
        daily_plans: List[Dict[str, Any]]
    ) -> bytes:
        """Generate a PDF itinerary document"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2E86AB')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=HexColor('#A23B72')
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=HexColor('#F18F01'),
            leftIndent=10
        )
        
        # Title Section
        trip_title = f"🌍 {destination} Adventure"
        story.append(Paragraph(trip_title, title_style))
        
        date_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(date_range, subtitle_style))
        
        story.append(Paragraph(f"Prepared for: {user_name}", styles['Normal']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#2E86AB')))
        story.append(Spacer(1, 20))

        # Trip Summary
        if trip_summary:
            story.append(Paragraph("📋 Trip Overview", section_style))
            story.append(Paragraph(trip_summary, styles['Normal']))
            story.append(Spacer(1, 15))

        # Flights Section
        if flights:
            story.append(Paragraph("✈️ Flight Information", section_style))
            for i, flight in enumerate(flights, 1):
                flight_info = self._format_flight_info(flight, i)
                story.append(Paragraph(flight_info, styles['Normal']))
                story.append(Spacer(1, 10))
            story.append(Spacer(1, 15))

        # Hotels Section  
        if hotels:
            story.append(Paragraph("🏨 Accommodation", section_style))
            for i, hotel in enumerate(hotels, 1):
                hotel_info = self._format_hotel_info(hotel, i)
                story.append(Paragraph(hotel_info, styles['Normal']))
                story.append(Spacer(1, 10))
            story.append(Spacer(1, 15))

        # Daily Itinerary
        if daily_plans:
            story.append(Paragraph("📅 Daily Itinerary", section_style))
            for day_plan in daily_plans:
                day_info = self._format_daily_plan(day_plan)
                story.append(Paragraph(day_info, styles['Normal']))
                story.append(Spacer(1, 12))

        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 10))
        footer_text = "✨ Have an amazing trip! Safe travels! ✨<br/>Generated by RouteRishi"
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph(footer_text, footer_style))

        try:
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            return pdf_bytes
        except Exception as e:
            logger.error(f"Failed to build PDF: {e}")
            raise
        finally:
            buffer.close()

    def _format_flight_info(self, flight: Dict[str, Any], index: int) -> str:
        """Format flight information for PDF"""
        try:
            price = flight.get('Price', 'N/A')
            route = flight.get('Route', 'N/A')
            airline = flight.get('Airline', 'N/A')
            
            result = f"<b>Flight {index}:</b><br/>"
            result += f"• Route: {route}<br/>"
            result += f"• Airline: {airline}<br/>"
            result += f"💰 Price: {price}"
            
            return result
        except Exception as e:
            logger.error(f"Error formatting flight info: {e}")
            return f"<b>Flight {index}:</b> Details unavailable"

    def _format_hotel_info(self, hotel: Dict[str, Any], index: int) -> str:
        """Format hotel information for PDF"""
        try:
            name = hotel.get('Hotel Name', 'Hotel Name Unavailable')
            total_price = hotel.get('Total price for stay', 'N/A')
            location = hotel.get('Location', 'N/A')
            
            result = f"<b>Hotel {index}: {name}</b><br/>"
            result += f"• Location: {location}<br/>"
            result += f"💰 Total Price: {total_price}"
            
            return result
        except Exception as e:
            logger.error(f"Error formatting hotel info: {e}")
            return f"<b>Hotel {index}:</b> Details unavailable"

    def _format_daily_plan(self, day_plan: Dict[str, Any]) -> str:
        """Format daily plan information for PDF"""
        try:
            if day_plan:
                day_key = list(day_plan.keys())[0]
                day_content = day_plan[day_key]
                
                result = f"<b>{day_key}</b><br/>"
                result += f"{day_content}<br/>"
            else:
                result = "<b>Day plan:</b> Details unavailable<br/>"
            
            return result
        except Exception as e:
            logger.error(f"Error formatting daily plan: {e}")
            return f"<b>Day plan:</b> Details unavailable"

    async def upload_pdf_to_firebase(self, pdf_bytes: bytes, filename: str) -> str:
        """Upload PDF to Firebase Storage and return public URL"""
        try:
            unique_filename = f"itineraries/{filename}_{uuid.uuid4().hex[:8]}.pdf"
            
            # Upload to Firebase Storage
            blob = self.bucket.blob(unique_filename)
            blob.upload_from_string(pdf_bytes, content_type='application/pdf')
            
            try:
                blob.make_public()
                public_url = blob.public_url
            except Exception as e:
                logger.warning(
                    "Could not make blob public, falling back to signed URL: %s", e
                )
                public_url = blob.generate_signed_url(expiration=timedelta(days=7))
            logger.info(f"PDF uploaded successfully: {unique_filename}")
            
            return public_url
        except Exception as e:
            logger.error(f"Failed to upload PDF to Firebase: {e}")
            raise

    async def delete_pdf_from_firebase(self, pdf_url: str) -> bool:
        """Delete PDF from Firebase Storage"""
        try:
            # Extract filename from URL
            filename = pdf_url.split('/')[-1].split('?')[0]  # Remove query params
            blob = self.bucket.blob(f"itineraries/{filename}")
            blob.delete()
            logger.info(f"PDF deleted successfully: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete PDF: {e}")
            return False

    async def create_and_save_itinerary_pdf(
        self,
        trip_summary: str,
        user_name: str,
        destination: str,
        start_date: date,
        end_date: date,
        flights: List[Dict[str, Any]],
        hotels: List[Dict[str, Any]],
        daily_plans: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create PDF and upload to Firebase Storage"""
        try:
            logger.info("Starting PDF creation process...")
            
            # Generate PDF
            pdf_bytes = self.create_itinerary_pdf(
                trip_summary, user_name, destination, start_date, end_date,
                flights, hotels, daily_plans
            )
            
            pdf_size = len(pdf_bytes)
            file_size_mb = pdf_size / (1024 * 1024)
            
            if pdf_size == 0:
                logger.error("Generated PDF has zero bytes!")
                raise ValueError("Generated PDF has zero bytes")
            
            # Create filename
            safe_destination = destination.replace(' ', '_').replace(',', '')
            filename = f"{safe_destination}_{start_date.strftime('%Y%m%d')}"
            
            # Upload to Firebase
            logger.info("Uploading to Firebase...")
            pdf_url = await self.upload_pdf_to_firebase(pdf_bytes, filename)
            logger.info(f"Upload successful, got URL: {pdf_url}")
            
            result = {
                "pdf_url": pdf_url,
                "filename": f"{filename}.pdf",
                "file_size_mb": round(file_size_mb, 4),
                "created_at": datetime.now(),
                "success": True
            }
            return result
            
        except Exception as e:
            logger.error(f"Failed to create and save PDF: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_pdf_service = None

def get_pdf_service() -> PDFService:
    """Dependency injection for PDFService"""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFService()
    return _pdf_service

