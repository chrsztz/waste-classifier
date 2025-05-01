import React from 'react';
import { FaTrash, FaGlassWhiskey, FaFileAlt, FaCog } from 'react-icons/fa';

const BinLevels = ({ binLevels }) => {
  // Function to determine color based on fill level
  const getFillColor = (type, percentage) => {
    // Error reading or no reading
    if (percentage < 0) return 'bg-gray-300';
    
    // Base color for each bin type
    const baseColors = {
      paper: 'bg-paper',
      glass: 'bg-glass',
      metal: 'bg-metal',
      others: 'bg-others'
    };
    
    // Add opacity based on fill level
    return baseColors[type];
  };
  
  // Function to get icon based on bin type
  const getBinIcon = (type) => {
    switch (type) {
      case 'paper':
        return <FaFileAlt className="text-yellow-700" />;
      case 'glass':
        return <FaGlassWhiskey className="text-blue-700" />;
      case 'metal':
        return <FaCog className="text-gray-700" />;
      case 'others':
        return <FaTrash className="text-green-700" />;
      default:
        return <FaTrash />;
    }
  };
  
  return (
    <div className="bg-white p-6 rounded-xl shadow-md">
      <h2 className="text-2xl font-bold text-center mb-6">Bin Fill Levels</h2>
      
      <div className="grid grid-cols-4 gap-4">
        {Object.entries(binLevels).map(([binType, percentage]) => (
          <div key={binType} className="flex flex-col items-center">
            <div className="mb-2 text-xl flex items-center gap-2">
              {getBinIcon(binType)}
              <span className="capitalize">{binType}</span>
            </div>
            
            <div className="w-full h-48 bg-gray-200 rounded-lg overflow-hidden relative">
              {/* Fill level visualization */}
              <div 
                className={`absolute bottom-0 left-0 right-0 ${getFillColor(binType, percentage)} transition-all duration-500`}
                style={{ 
                  height: `${percentage < 0 ? 0 : percentage}%`,
                }}
              ></div>
              
              {/* Percentage text */}
              <div className="absolute inset-0 flex items-center justify-center font-bold text-2xl">
                {percentage < 0 ? 'N/A' : `${Math.round(percentage)}%`}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BinLevels; 