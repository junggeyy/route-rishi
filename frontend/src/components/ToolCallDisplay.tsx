import React from 'react';
import { Plane, MapPin, DollarSign, CloudSun, Calendar, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import type { ToolCall } from '../types';

interface ToolCallDisplayProps {
  toolCalls: ToolCall[];
  executionTimeMs?: number;
}

const getToolIcon = (toolName: string) => {
  switch (toolName) {
    case 'Flight Search':
      return <Plane className="w-4 h-4" />;
    case 'Hotel Search':
      return <MapPin className="w-4 h-4" />;
    case 'Weather Forecast':
      return <CloudSun className="w-4 h-4" />;
    case 'Currency Exchange':
      return <DollarSign className="w-4 h-4" />;
    case 'Current Date':
      return <Calendar className="w-4 h-4" />;
    default:
      return <CheckCircle2 className="w-4 h-4" />;
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircle2 className="w-3 h-3 text-green-400" />;
    case 'running':
      return <Loader2 className="w-3 h-3 text-accent animate-spin" />;
    case 'error':
      return <AlertCircle className="w-3 h-3 text-red-400" />;
    default:
      return <CheckCircle2 className="w-3 h-3 text-green-400" />;
  }
};

const formatInputParams = (params: Record<string, any>): string => {
  const formatted = Object.entries(params)
    .map(([key, value]) => {
      // Make keys more readable
      const readableKey = key
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .toLowerCase()
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      
      return `${readableKey}: ${value}`;
    })
    .join(', ');
  
  return formatted.length > 100 ? formatted.slice(0, 100) + '...' : formatted;
};

export const ToolCallDisplay: React.FC<ToolCallDisplayProps> = ({ 
  toolCalls, 
  executionTimeMs 
}) => {
  if (!toolCalls || toolCalls.length === 0) return null;

  return (
    <div className="space-y-2 mb-3">
      {/* Execution time badge */}
      {executionTimeMs && (
        <div className="flex justify-start">
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-secondary/50 text-gray-300">
            ⚡ Completed in {(executionTimeMs / 1000).toFixed(1)}s
          </span>
        </div>
      )}
      
      {/* Tool calls */}
      {toolCalls.map((toolCall, index) => (
        <div 
          key={index}
          className="flex items-start space-x-3 p-3 rounded-lg bg-secondary/30 border border-secondary/50"
        >
          {/* Tool icon */}
          <div className="flex-shrink-0 mt-0.5">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-accent/20 text-accent">
              {getToolIcon(toolCall.tool_name)}
            </div>
          </div>
          
          {/* Tool details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h4 className="text-sm font-medium text-white">
                {toolCall.tool_name}
              </h4>
              {getStatusIcon(toolCall.status)}
            </div>
            
            {/* Input parameters */}
            <p className="text-xs text-gray-300 mt-1">
              {formatInputParams(toolCall.input_params)}
            </p>
            
            {/* Output summary for completed calls */}
            {toolCall.status === 'completed' && toolCall.output && (
              <div className="mt-2">
                <p className="text-xs text-gray-400 line-clamp-2">
                  {toolCall.output.length > 150 
                    ? `${toolCall.output.slice(0, 150)}...` 
                    : toolCall.output
                  }
                </p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}; 