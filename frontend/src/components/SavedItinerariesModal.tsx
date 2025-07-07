import React, { useState, useEffect } from 'react';
import { X, MoreHorizontal, Trash2, Download, Calendar, MapPin, FileText } from 'lucide-react';
import { itineraryApi } from '../services/api';
import { authService } from '../services/authService';
import type { SavedItinerary } from '../types';

interface SavedItinerariesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SavedItinerariesModal: React.FC<SavedItinerariesModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [itineraries, setItineraries] = useState<SavedItinerary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showOptions, setShowOptions] = useState<string | null>(null);
  const [showDeleteAllConfirm, setShowDeleteAllConfirm] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchItineraries();
    }
  }, [isOpen]);

  const fetchItineraries = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = authService.getStoredToken();
      if (!token) {
        setError('Not authenticated');
        return;
      }
      
      const data = await itineraryApi.getSavedItineraries(token);
      setItineraries(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load saved itineraries');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItinerary = async (id: string) => {
    try {
      const token = authService.getStoredToken();
      if (!token) return;
      
      await itineraryApi.deleteSavedItinerary(token, id);
      setItineraries(prev => prev.filter(item => item.id !== id));
      setShowOptions(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete itinerary');
    }
  };

  const handleDeleteAll = async () => {
    try {
      const token = authService.getStoredToken();
      if (!token) return;
      
      await itineraryApi.deleteAllSavedItineraries(token);
      setItineraries([]);
      setShowOptions(null);
      setShowDeleteAllConfirm(false);
    } catch (err: any) {
      setError(err.message || 'Failed to delete all itineraries');
    }
  };

  const handleDownload = (pdfUrl: string, title: string) => {
    window.open(pdfUrl, '_blank');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString([], {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatFileSize = (sizeInMB: number) => {
    if (sizeInMB < 1) {
      return `${Math.round(sizeInMB * 1024)} KB`;
    }
    return `${sizeInMB.toFixed(1)} MB`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card rounded-xl max-w-2xl w-full max-h-[80vh] overflow-hidden relative">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border/50">
          <h2 className="text-xl font-bold text-text-primary">Saved Itineraries</h2>
          <div className="flex items-center space-x-2">
            {/* Delete All Button */}
            {itineraries.length > 0 && (
              <button
                onClick={() => setShowDeleteAllConfirm(true)}
                className="p-2 text-text-secondary hover:text-danger transition-colors"
                title="Delete all itineraries"
              >
                <MoreHorizontal className="w-5 h-5" />
              </button>
            )}
            
            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 text-text-secondary hover:text-text-primary transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-text-secondary">Loading saved itineraries...</p>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-danger/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <X className="w-8 h-8 text-danger" />
              </div>
              <p className="text-danger mb-4">{error}</p>
              <button
                onClick={fetchItineraries}
                className="button-secondary"
              >
                Try Again
              </button>
            </div>
          ) : itineraries.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-secondary/50 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-text-secondary" />
              </div>
              <p className="text-text-secondary text-lg">No itineraries saved</p>
              <p className="text-text-secondary/70 text-sm mt-2">
                Create your first itinerary by planning a trip with RouteRishi!
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {itineraries.map((itinerary, index) => (
                <div
                  key={itinerary.id}
                  className="bg-secondary/30 rounded-lg p-4 hover:bg-secondary/50 transition-colors relative"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      {/* Number and Title */}
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="bg-accent/20 text-accent text-sm font-medium px-2 py-1 rounded">
                          {index + 1}
                        </span>
                        <h3 className="text-text-primary font-medium truncate">
                          {itinerary.title}
                        </h3>
                      </div>
                      
                      {/* Details */}
                      <div className="flex items-center space-x-4 text-sm text-text-secondary mb-3">
                        <div className="flex items-center space-x-1">
                          <MapPin className="w-4 h-4" />
                          <span>{itinerary.destination}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>
                            {formatDate(itinerary.start_date)} - {formatDate(itinerary.end_date)}
                          </span>
                        </div>
                      </div>
                      
                      {/* File Info */}
                      <div className="flex items-center space-x-4 text-xs text-text-secondary">
                        <span>Created: {formatDate(itinerary.created_at)}</span>
                        <span>Size: {formatFileSize(itinerary.file_size_mb)}</span>
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleDownload(itinerary.pdf_url, itinerary.title)}
                        className="p-2 text-text-secondary hover:text-accent transition-colors"
                        title="Download PDF"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      
                      <div className="relative">
                        <button
                          onClick={() => setShowOptions(showOptions === itinerary.id ? null : itinerary.id)}
                          className="p-2 text-text-secondary hover:text-text-primary transition-colors"
                          title="More options"
                        >
                          <MoreHorizontal className="w-4 h-4" />
                        </button>
                        
                        {/* Options Dropdown */}
                        {showOptions === itinerary.id && (
                          <>
                            <div className="absolute right-0 top-full mt-1 bg-secondary/90 backdrop-blur-xl rounded-lg shadow-lg py-2 z-10 min-w-[120px]">
                              <button
                                onClick={() => handleDeleteItinerary(itinerary.id)}
                                className="flex items-center space-x-2 w-full px-3 py-2 text-danger hover:bg-danger/20 transition-colors"
                              >
                                <Trash2 className="w-4 h-4" />
                                <span>Delete</span>
                              </button>
                            </div>
                            <div 
                              className="fixed inset-0 z-5"
                              onClick={() => setShowOptions(null)}
                            />
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Click outside to close */}
      <div 
        className="absolute inset-0 -z-10"
        onClick={onClose}
      />
      
      {/* Delete All Confirmation Dialog */}
      {showDeleteAllConfirm && (
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-10">
          <div className="glass-card rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-text-primary mb-2">Delete All Itineraries</h3>
            <p className="text-text-secondary mb-6">
              Are you sure you want to delete all saved itineraries? This action cannot be undone.
            </p>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowDeleteAllConfirm(false)}
                className="button-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAll}
                className="bg-danger hover:bg-danger/90 text-white px-4 py-2 rounded-lg transition-colors flex-1"
              >
                Delete All
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 