import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import BinLevels from './components/BinLevels';
import ClassificationResult from './components/ClassificationResult';
import Header from './components/Header';
import HistoryList from './components/HistoryList';
import AdminPanel from './components/AdminPanel';
import { FaLock, FaUnlock } from 'react-icons/fa';

// Initialize socket connection
const socket = io(process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000');

const App = () => {
  // State
  const [binLevels, setBinLevels] = useState({
    paper: 0,
    glass: 0,
    metal: 0,
    others: 0
  });
  
  const [classificationResult, setClassificationResult] = useState(null);
  const [classificationHistory, setClassificationHistory] = useState([]);
  const [systemStatus, setSystemStatus] = useState('idle'); // 'idle', 'classifying', 'error'
  const [showHistory, setShowHistory] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  
  // Fetch initial bin levels and classification history
  useEffect(() => {
    // Fetch bin levels
    axios.get('/api/bin_levels')
      .then(response => {
        if (!response.data.error) {
          setBinLevels(response.data);
        }
      })
      .catch(error => console.error('Error fetching bin levels:', error));
    
    // Fetch classification history
    axios.get('/api/history')
      .then(response => {
        setClassificationHistory(response.data);
      })
      .catch(error => console.error('Error fetching history:', error));
    
    // Socket.io event listeners
    socket.on('connect', () => {
      console.log('Connected to server');
    });
    
    socket.on('bin_levels', (levels) => {
      setBinLevels(levels);
    });
    
    socket.on('classification_result', (result) => {
      setClassificationResult(result);
      setSystemStatus('idle');
      
      // Add to history (only if we don't already have this result)
      setClassificationHistory(prevHistory => {
        const exists = prevHistory.some(item => item.timestamp === result.timestamp);
        if (!exists) {
          return [result, ...prevHistory];
        }
        return prevHistory;
      });
    });
    
    socket.on('correction_result', (result) => {
      if (result.success) {
        // Update the history with the corrected classification
        setClassificationHistory(prevHistory => {
          const updatedHistory = prevHistory.map(item => {
            if (item.timestamp === classificationResult.timestamp) {
              return {
                ...item,
                class: classificationResult.class,
                corrected: true,
                original_class: classificationResult.original_class
              };
            }
            return item;
          });
          return updatedHistory;
        });
      }
    });
    
    // Cleanup on unmount
    return () => {
      socket.off('connect');
      socket.off('bin_levels');
      socket.off('classification_result');
      socket.off('correction_result');
    };
  }, []);
  
  // Handle manual classification request
  const handleManualClassify = () => {
    setSystemStatus('classifying');
    setClassificationResult(null);
    
    socket.emit('request_manual_classification');
  };
  
  // Handle classification correction
  const handleCorrectClassification = (timestamp, newClass) => {
    socket.emit('correct_classification', {
      timestamp,
      class: newClass
    });
    
    // Update UI immediately (optimistic update)
    setClassificationResult(prev => {
      if (prev && prev.timestamp === timestamp) {
        return {
          ...prev,
          class: newClass,
          corrected: true,
          original_class: prev.class
        };
      }
      return prev;
    });
  };
  
  // Toggle history view
  const toggleHistory = () => {
    setShowHistory(prev => !prev);
  };
  
  // Toggle admin login
  const toggleAdminLogin = () => {
    setShowAdminLogin(prev => !prev);
    if (!showAdminLogin) {
      setAdminPassword('');
      setIsAdminAuthenticated(false);
    }
  };
  
  // Handle admin password input
  const handleAdminPasswordChange = (e) => {
    setAdminPassword(e.target.value);
  };
  
  // Validate admin password
  const handleAdminLogin = (e) => {
    e.preventDefault();
    // Simple password check - in a real system, use secure authentication
    if (adminPassword === 'admin123') {
      setIsAdminAuthenticated(true);
      setShowAdmin(true);
      setShowAdminLogin(false);
    } else {
      alert('Invalid password');
    }
  };
  
  // Toggle admin panel
  const toggleAdminPanel = () => {
    if (isAdminAuthenticated) {
      setShowAdmin(prev => !prev);
    } else {
      setShowAdminLogin(true);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <Header systemStatus={systemStatus} />
      
      <main className="container mx-auto px-4 py-6">
        {/* Admin login modal */}
        {showAdminLogin && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-xl w-80">
              <h3 className="text-xl font-medium mb-4">Admin Login</h3>
              <form onSubmit={handleAdminLogin}>
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                    Password
                  </label>
                  <input 
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                    id="password" 
                    type="password" 
                    placeholder="Enter admin password"
                    value={adminPassword}
                    onChange={handleAdminPasswordChange}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <button
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    type="submit"
                  >
                    Login
                  </button>
                  <button
                    className="text-gray-500 hover:text-gray-700"
                    type="button"
                    onClick={toggleAdminLogin}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        
        {/* Admin toggle button */}
        <div className="flex justify-end mb-4">
          <button
            onClick={toggleAdminPanel}
            className={`flex items-center gap-2 py-2 px-4 rounded-lg ${
              isAdminAuthenticated ? 'bg-green-500 hover:bg-green-600 text-white' : 'bg-gray-300 hover:bg-gray-400 text-gray-700'
            }`}
          >
            {isAdminAuthenticated ? <FaUnlock /> : <FaLock />}
            {showAdmin ? 'Hide Admin Panel' : 'Admin Panel'}
          </button>
        </div>
        
        {/* Admin Panel (if authenticated) */}
        {showAdmin && isAdminAuthenticated && (
          <AdminPanel />
        )}
        
        {/* Bin Levels Display */}
        <BinLevels binLevels={binLevels} />
        
        {/* Classification Result or Idle Display */}
        {classificationResult ? (
          <ClassificationResult 
            result={classificationResult} 
            onCorrect={handleCorrectClassification}
          />
        ) : (
          <div className="my-8 text-center">
            <h2 className="text-2xl font-bold text-gray-700 mb-4">
              {systemStatus === 'classifying' 
                ? 'Classifying waste...' 
                : 'Waiting for waste...'}
            </h2>
            <button
              onClick={handleManualClassify}
              disabled={systemStatus === 'classifying'}
              className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-6 rounded-lg disabled:opacity-50"
            >
              Manual Classification
            </button>
          </div>
        )}
        
        {/* History Toggle Button */}
        <div className="text-center mt-8">
          <button 
            onClick={toggleHistory}
            className="bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg"
          >
            {showHistory ? 'Hide History' : 'Show History'}
          </button>
        </div>
        
        {/* Classification History */}
        {showHistory && (
          <HistoryList 
            history={classificationHistory} 
            onCorrect={handleCorrectClassification}
          />
        )}
      </main>
      
      <footer className="bg-gray-800 text-white py-4 text-center">
        <p>Waste Classification System - Powered by YOLOv11s-cls</p>
      </footer>
    </div>
  );
};

export default App; 