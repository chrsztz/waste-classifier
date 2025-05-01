import React from 'react';
import { FaTrash, FaGlassWhiskey, FaFileAlt, FaCog, FaEdit } from 'react-icons/fa';

const HistoryList = ({ history, onCorrect }) => {
  // Function to format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return timestamp;
    }
  };
  
  // Function to get icon based on waste type
  const getWasteIcon = (type) => {
    switch (type.toLowerCase()) {
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
  
  // Function to get background color based on waste type
  const getWasteColor = (type) => {
    switch (type.toLowerCase()) {
      case 'paper':
        return 'bg-paper/20';
      case 'glass':
        return 'bg-glass/20';
      case 'metal':
        return 'bg-metal/20';
      case 'others':
        return 'bg-others/20';
      default:
        return 'bg-gray-100';
    }
  };
  
  // Handle correction button click to open correction modal
  const handleCorrection = (item) => {
    // For now, just show options in a dropdown or modal
    // This would be expanded in a real implementation
    console.log('Correct classification for:', item);
  };
  
  return (
    <div className="mt-8 bg-white p-6 rounded-xl shadow-md">
      <h2 className="text-2xl font-bold text-center mb-6">Classification History</h2>
      
      {history.length === 0 ? (
        <p className="text-center text-gray-500">No classification history yet.</p>
      ) : (
        <div className="overflow-auto max-h-96">
          <table className="min-w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-3 px-4 text-left">Time</th>
                <th className="py-3 px-4 text-left">Classification</th>
                <th className="py-3 px-4 text-left">Confidence</th>
                <th className="py-3 px-4 text-left">Correction</th>
                <th className="py-3 px-4 text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {history.map((item, index) => (
                <tr 
                  key={item.timestamp || index} 
                  className={`${getWasteColor(item.class)} hover:bg-gray-50`}
                >
                  <td className="py-3 px-4">{formatTimestamp(item.timestamp)}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      {getWasteIcon(item.class)}
                      <span className="capitalize">{item.class}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    {item.confidence ? `${(item.confidence * 100).toFixed(1)}%` : 'N/A'}
                  </td>
                  <td className="py-3 px-4">
                    {item.corrected ? (
                      <div className="flex items-center gap-2 text-gray-600">
                        <span>Corrected from:</span>
                        <div className="flex items-center gap-1">
                          {getWasteIcon(item.original_class)}
                          <span className="capitalize">{item.original_class}</span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-gray-500">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <button 
                      onClick={() => handleCorrection(item)}
                      className="p-2 text-blue-600 hover:text-blue-800 rounded-full hover:bg-blue-100"
                      title="Correct Classification"
                    >
                      <FaEdit />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default HistoryList; 