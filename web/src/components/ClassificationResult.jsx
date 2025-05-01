import React from 'react';
import { FaTrash, FaGlassWhiskey, FaFileAlt, FaCog, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

const ClassificationResult = ({ result, onCorrect }) => {
  // Function to format confidence as percentage
  const formatConfidence = (confidence) => {
    return `${(confidence * 100).toFixed(1)}%`;
  };
  
  // Function to get icon based on waste type
  const getWasteIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'paper':
        return <FaFileAlt className="text-yellow-700 text-4xl" />;
      case 'glass':
        return <FaGlassWhiskey className="text-blue-700 text-4xl" />;
      case 'metal':
        return <FaCog className="text-gray-700 text-4xl" />;
      case 'others':
        return <FaTrash className="text-green-700 text-4xl" />;
      default:
        return <FaTrash className="text-4xl" />;
    }
  };
  
  // Function to get color based on waste type
  const getWasteColor = (type) => {
    switch (type.toLowerCase()) {
      case 'paper':
        return 'border-paper bg-yellow-50';
      case 'glass':
        return 'border-glass bg-blue-50';
      case 'metal':
        return 'border-metal bg-gray-50';
      case 'others':
        return 'border-others bg-green-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };
  
  // Handle correction button click
  const handleCorrection = (newClass) => {
    if (onCorrect && result.timestamp) {
      onCorrect(result.timestamp, newClass);
    }
  };
  
  return (
    <div className="my-8">
      <h2 className="text-2xl font-bold text-center mb-6">Classification Result</h2>
      
      {/* Main result card */}
      <div className={`p-6 rounded-xl shadow-md border-4 ${getWasteColor(result.class)} mb-6`}>
        <div className="flex items-center justify-center gap-8">
          {/* Icon and classification */}
          <div className="flex flex-col items-center">
            {getWasteIcon(result.class)}
            <h3 className="text-2xl font-bold mt-3 capitalize">{result.class}</h3>
            <p className="text-gray-500">
              Confidence: {formatConfidence(result.confidence)}
            </p>
          </div>
          
          {/* Image preview (if available) */}
          {result.image_path && (
            <div className="w-64 h-64 bg-gray-200 rounded-lg overflow-hidden">
              <img 
                src={`/captured_images/${result.image_path.split('/').pop()}`} 
                alt="Classified waste"
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://via.placeholder.com/256?text=Image+Not+Available';
                }}
              />
            </div>
          )}
        </div>
      </div>
      
      {/* Correction section */}
      <div className="bg-white p-6 rounded-xl shadow-md">
        <div className="text-center mb-4">
          <h3 className="text-xl font-bold">Is this classification correct?</h3>
          <div className="flex justify-center gap-4 mt-3">
            <button className="flex items-center gap-2 py-2 px-4 bg-green-500 text-white rounded-lg hover:bg-green-600">
              <FaCheckCircle />
              Yes, it's correct
            </button>
            <button className="flex items-center gap-2 py-2 px-4 bg-red-500 text-white rounded-lg hover:bg-red-600">
              <FaTimesCircle />
              No, it's wrong
            </button>
          </div>
        </div>
        
        <div className="mt-6">
          <p className="text-center font-medium mb-4">If incorrect, select the right category:</p>
          <div className="grid grid-cols-4 gap-4">
            <button 
              onClick={() => handleCorrection('paper')}
              className={`p-4 rounded-lg flex flex-col items-center gap-2 ${result.class === 'paper' ? 'bg-paper' : 'bg-gray-100 hover:bg-paper/20'}`}
            >
              <FaFileAlt className="text-2xl text-yellow-700" />
              <span>Paper</span>
            </button>
            
            <button 
              onClick={() => handleCorrection('glass')}
              className={`p-4 rounded-lg flex flex-col items-center gap-2 ${result.class === 'glass' ? 'bg-glass' : 'bg-gray-100 hover:bg-glass/20'}`}
            >
              <FaGlassWhiskey className="text-2xl text-blue-700" />
              <span>Glass</span>
            </button>
            
            <button 
              onClick={() => handleCorrection('metal')}
              className={`p-4 rounded-lg flex flex-col items-center gap-2 ${result.class === 'metal' ? 'bg-metal' : 'bg-gray-100 hover:bg-metal/20'}`}
            >
              <FaCog className="text-2xl text-gray-700" />
              <span>Metal</span>
            </button>
            
            <button 
              onClick={() => handleCorrection('others')}
              className={`p-4 rounded-lg flex flex-col items-center gap-2 ${result.class === 'others' ? 'bg-others' : 'bg-gray-100 hover:bg-others/20'}`}
            >
              <FaTrash className="text-2xl text-green-700" />
              <span>Others</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClassificationResult; 