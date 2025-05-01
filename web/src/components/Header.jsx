import React from 'react';
import { FaRecycle, FaCircle } from 'react-icons/fa';

const Header = ({ systemStatus }) => {
  // Get status indicator color
  const getStatusColor = () => {
    switch (systemStatus) {
      case 'classifying':
        return 'text-yellow-500';
      case 'error':
        return 'text-red-500';
      case 'idle':
      default:
        return 'text-green-500';
    }
  };
  
  // Get status text
  const getStatusText = () => {
    switch (systemStatus) {
      case 'classifying':
        return 'Classifying';
      case 'error':
        return 'Error';
      case 'idle':
      default:
        return 'Ready';
    }
  };
  
  return (
    <header className="bg-gray-800 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center gap-3">
          <FaRecycle className="text-3xl text-green-400" />
          <h1 className="text-2xl font-bold">Waste Classification System</h1>
        </div>
        
        <div className="flex items-center gap-2">
          <FaCircle className={`${getStatusColor()} animate-pulse`} />
          <span>{getStatusText()}</span>
        </div>
      </div>
    </header>
  );
};

export default Header; 