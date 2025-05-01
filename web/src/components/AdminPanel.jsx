import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaTrash, FaGlassWhiskey, FaFileAlt, FaCog, FaChartPie, FaTable, FaImage, FaEye } from 'react-icons/fa';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const AdminPanel = () => {
  const [history, setHistory] = useState([]);
  const [statistics, setStatistics] = useState({
    total: 0,
    correct: 0,
    corrected: 0,
    byCategory: {
      paper: 0,
      glass: 0,
      metal: 0,
      others: 0
    },
    byOriginalClass: {
      cardboard: 0,
      glass: 0,
      metal: 0,
      paper: 0,
      plastic: 0,
      trash: 0
    }
  });
  const [binLevels, setBinLevels] = useState({
    paper: 0,
    glass: 0,
    metal: 0,
    others: 0
  });
  const [activeTab, setActiveTab] = useState('statistics');
  const [selectedImage, setSelectedImage] = useState(null);
  
  // Fetch data on component mount
  useEffect(() => {
    // Fetch classification history
    axios.get('/api/history')
      .then(response => {
        setHistory(response.data);
        calculateStatistics(response.data);
      })
      .catch(error => console.error('Error fetching history:', error));
    
    // Fetch bin levels
    axios.get('/api/bin_levels')
      .then(response => {
        if (!response.data.error) {
          setBinLevels(response.data);
        }
      })
      .catch(error => console.error('Error fetching bin levels:', error));
  }, []);
  
  // Calculate statistics from history data
  const calculateStatistics = (data) => {
    if (!data || data.length === 0) return;
    
    const stats = {
      total: data.length,
      correct: 0,
      corrected: 0,
      byCategory: {
        paper: 0,
        glass: 0,
        metal: 0,
        others: 0
      },
      byOriginalClass: {
        cardboard: 0,
        glass: 0,
        metal: 0,
        paper: 0,
        plastic: 0,
        trash: 0
      }
    };
    
    // Process each classification
    data.forEach(item => {
      // Count by final bin category
      if (item.class) {
        stats.byCategory[item.class] = (stats.byCategory[item.class] || 0) + 1;
      }
      
      // Count by original model class
      if (item.original_class) {
        stats.byOriginalClass[item.original_class] = 
          (stats.byOriginalClass[item.original_class] || 0) + 1;
      }
      
      // Count corrections
      if (item.corrected) {
        stats.corrected += 1;
      } else {
        stats.correct += 1;
      }
    });
    
    setStatistics(stats);
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return timestamp;
    }
  };
  
  // Get icon for waste type
  const getWasteIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'paper':
      case 'cardboard':
        return <FaFileAlt className="text-yellow-700" />;
      case 'glass':
        return <FaGlassWhiskey className="text-blue-700" />;
      case 'metal':
        return <FaCog className="text-gray-700" />;
      case 'others':
      case 'plastic':
      case 'trash':
        return <FaTrash className="text-green-700" />;
      default:
        return <FaTrash />;
    }
  };
  
  // View image details
  const viewImageDetails = (item) => {
    setSelectedImage(item);
  };
  
  // Close image modal
  const closeImageModal = () => {
    setSelectedImage(null);
  };
  
  // Pie chart data for bin categories
  const categoryPieData = {
    labels: Object.keys(statistics.byCategory).map(cat => cat.charAt(0).toUpperCase() + cat.slice(1)),
    datasets: [
      {
        label: 'Classifications by Bin Category',
        data: Object.values(statistics.byCategory),
        backgroundColor: [
          '#fcd34d', // paper - yellow
          '#60a5fa', // glass - blue
          '#9ca3af', // metal - gray
          '#a3e635', // others - green
        ],
        borderWidth: 1,
      },
    ],
  };
  
  // Pie chart data for original model classes
  const originalClassPieData = {
    labels: Object.keys(statistics.byOriginalClass).map(cls => cls.charAt(0).toUpperCase() + cls.slice(1)),
    datasets: [
      {
        label: 'Classifications by Original Class',
        data: Object.values(statistics.byOriginalClass),
        backgroundColor: [
          '#f97316', // cardboard - orange
          '#60a5fa', // glass - blue
          '#9ca3af', // metal - gray
          '#fcd34d', // paper - yellow
          '#10b981', // plastic - green
          '#6b7280', // trash - dark gray
        ],
        borderWidth: 1,
      },
    ],
  };
  
  // Bar chart data for accuracy
  const accuracyBarData = {
    labels: ['Correct', 'Corrected'],
    datasets: [
      {
        label: 'Classification Accuracy',
        data: [statistics.correct, statistics.corrected],
        backgroundColor: [
          '#4ade80', // correct - green
          '#f87171', // corrected - red
        ],
        borderWidth: 1,
      },
    ],
  };
  
  // Bar chart options
  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Classification Accuracy',
      },
    },
  };
  
  return (
    <div className="bg-white p-6 rounded-xl shadow-md mb-6">
      <h2 className="text-2xl font-bold text-center mb-6">Admin Panel</h2>
      
      {/* Tab navigation */}
      <div className="flex border-b mb-6">
        <button
          className={`py-2 px-4 ${activeTab === 'statistics' ? 'text-blue-600 border-b-2 border-blue-600 font-medium' : 'text-gray-500 hover:text-blue-500'}`}
          onClick={() => setActiveTab('statistics')}
        >
          <FaChartPie className="inline mr-2" />
          Statistics
        </button>
        <button
          className={`py-2 px-4 ${activeTab === 'details' ? 'text-blue-600 border-b-2 border-blue-600 font-medium' : 'text-gray-500 hover:text-blue-500'}`}
          onClick={() => setActiveTab('details')}
        >
          <FaTable className="inline mr-2" />
          Classification Details
        </button>
      </div>
      
      {/* Statistics tab */}
      {activeTab === 'statistics' && (
        <div>
          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium mb-4 text-center">Bin Fill Levels</h3>
              <div className="grid grid-cols-4 gap-2">
                {Object.entries(binLevels).map(([binType, percentage]) => (
                  <div key={binType} className="flex flex-col items-center">
                    <div className="flex items-center gap-1">
                      {getWasteIcon(binType)}
                      <span className="capitalize text-sm">{binType}</span>
                    </div>
                    <div className="w-full h-20 bg-gray-200 rounded overflow-hidden relative mt-1">
                      <div 
                        className={`absolute bottom-0 left-0 right-0 ${
                          binType === 'paper' ? 'bg-paper' : 
                          binType === 'glass' ? 'bg-glass' : 
                          binType === 'metal' ? 'bg-metal' : 'bg-others'
                        }`}
                        style={{ height: `${percentage < 0 ? 0 : percentage}%` }}
                      ></div>
                      <div className="absolute inset-0 flex items-center justify-center text-sm font-bold">
                        {percentage < 0 ? 'N/A' : `${Math.round(percentage)}%`}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium mb-4 text-center">Classification Summary</h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-white p-3 rounded shadow">
                  <div className="text-3xl font-bold text-gray-700">{statistics.total}</div>
                  <div className="text-sm text-gray-500">Total Classifications</div>
                </div>
                <div className="bg-white p-3 rounded shadow">
                  <div className="text-3xl font-bold text-green-600">{statistics.correct}</div>
                  <div className="text-sm text-gray-500">Correct</div>
                </div>
                <div className="bg-white p-3 rounded shadow">
                  <div className="text-3xl font-bold text-red-500">{statistics.corrected}</div>
                  <div className="text-sm text-gray-500">Corrected</div>
                </div>
              </div>
              
              <div className="mt-4">
                <h4 className="text-center text-gray-700 font-medium mb-2">Accuracy Rate</h4>
                <div className="relative pt-1">
                  <div className="flex mb-2 items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-green-600 bg-green-200">
                        {statistics.total ? Math.round((statistics.correct / statistics.total) * 100) : 0}%
                      </span>
                    </div>
                  </div>
                  <div className="flex h-2 overflow-hidden text-xs bg-gray-200 rounded">
                    <div 
                      style={{ width: `${statistics.total ? (statistics.correct / statistics.total) * 100 : 0}%` }} 
                      className="bg-green-500"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium mb-4 text-center">Classifications by Bin</h3>
              <Pie data={categoryPieData} />
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium mb-4 text-center">Original Model Classes</h3>
              <Pie data={originalClassPieData} />
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium mb-4 text-center">Accuracy</h3>
              <Bar options={barOptions} data={accuracyBarData} />
            </div>
          </div>
        </div>
      )}
      
      {/* Details tab */}
      {activeTab === 'details' && (
        <div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Image
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Original Class
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Bin Category
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Corrected
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {history.map((item, index) => (
                  <tr key={item.timestamp || index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatTimestamp(item.timestamp)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {item.image_path ? (
                        <div className="h-12 w-12 bg-gray-200 rounded overflow-hidden">
                          <img 
                            src={`/captured_images/${item.image_path.split('/').pop()}`} 
                            alt="Classified waste"
                            className="h-full w-full object-cover"
                            onError={(e) => {
                              e.target.onerror = null;
                              e.target.src = 'https://via.placeholder.com/48?text=NA';
                            }}
                          />
                        </div>
                      ) : (
                        <span className="text-gray-400">No image</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="mr-2">{getWasteIcon(item.original_class)}</div>
                        <span className="capitalize">{item.original_class || 'Unknown'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="mr-2">{getWasteIcon(item.class)}</div>
                        <span className="capitalize">{item.class}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {item.confidence ? `${(item.confidence * 100).toFixed(1)}%` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {item.corrected ? (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                          Yes
                        </span>
                      ) : (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          No
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => viewImageDetails(item)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        <FaEye className="inline" /> View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {history.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No classification history available
            </div>
          )}
        </div>
      )}
      
      {/* Image details modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-screen overflow-auto">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-xl font-medium">Classification Details</h3>
              <button 
                onClick={closeImageModal}
                className="text-gray-500 hover:text-gray-700"
              >
                &times;
              </button>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-2 gap-6">
                {/* Image */}
                <div>
                  <h4 className="font-medium mb-2">Image</h4>
                  <div className="bg-gray-200 rounded-lg overflow-hidden h-64 w-full">
                    {selectedImage.image_path ? (
                      <img 
                        src={`/captured_images/${selectedImage.image_path.split('/').pop()}`} 
                        alt="Classified waste"
                        className="h-full w-full object-contain"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = 'https://via.placeholder.com/256?text=Image+Not+Available';
                        }}
                      />
                    ) : (
                      <div className="h-full w-full flex items-center justify-center text-gray-500">
                        <FaImage className="mr-2" /> No image available
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Classification details */}
                <div>
                  <h4 className="font-medium mb-2">Classification Information</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="grid grid-cols-2 gap-y-4">
                      <div className="font-medium">Time:</div>
                      <div>{formatTimestamp(selectedImage.timestamp)}</div>
                      
                      <div className="font-medium">Original Class:</div>
                      <div className="flex items-center">
                        {getWasteIcon(selectedImage.original_class)}
                        <span className="ml-1 capitalize">{selectedImage.original_class || 'Unknown'}</span>
                      </div>
                      
                      <div className="font-medium">Bin Category:</div>
                      <div className="flex items-center">
                        {getWasteIcon(selectedImage.class)}
                        <span className="ml-1 capitalize">{selectedImage.class}</span>
                      </div>
                      
                      <div className="font-medium">Confidence:</div>
                      <div>{selectedImage.confidence ? `${(selectedImage.confidence * 100).toFixed(1)}%` : 'N/A'}</div>
                      
                      <div className="font-medium">Corrected:</div>
                      <div>
                        {selectedImage.corrected ? (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                            Yes
                          </span>
                        ) : (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            No
                          </span>
                        )}
                      </div>
                      
                      {selectedImage.corrected && (
                        <>
                          <div className="font-medium">Original Prediction:</div>
                          <div className="flex items-center">
                            {getWasteIcon(selectedImage.original_class)}
                            <span className="ml-1 capitalize">{selectedImage.original_class}</span>
                          </div>
                        </>
                      )}
                    </div>
                    
                    {/* All scores */}
                    {selectedImage.all_scores && (
                      <div className="mt-6">
                        <h5 className="font-medium mb-2">Bin Category Scores</h5>
                        <div className="space-y-2">
                          {Object.entries(selectedImage.all_scores).map(([category, score]) => (
                            <div key={category} className="flex items-center">
                              <div className="w-20 capitalize">{category}:</div>
                              <div className="flex-1">
                                <div className="bg-gray-200 h-4 rounded-full overflow-hidden">
                                  <div 
                                    className={`h-full ${
                                      category === 'paper' ? 'bg-paper' : 
                                      category === 'glass' ? 'bg-glass' : 
                                      category === 'metal' ? 'bg-metal' : 'bg-others'
                                    }`}
                                    style={{ width: `${score * 100}%` }}
                                  ></div>
                                </div>
                              </div>
                              <div className="ml-2 w-16 text-right">{(score * 100).toFixed(1)}%</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Original scores if available */}
                    {selectedImage.original_scores && (
                      <div className="mt-6">
                        <h5 className="font-medium mb-2">Original Model Scores</h5>
                        <div className="space-y-2">
                          {Object.entries(selectedImage.original_scores).map(([className, score]) => (
                            <div key={className} className="flex items-center">
                              <div className="w-20 capitalize">{className}:</div>
                              <div className="flex-1">
                                <div className="bg-gray-200 h-4 rounded-full overflow-hidden">
                                  <div 
                                    className="h-full bg-blue-500"
                                    style={{ width: `${score * 100}%` }}
                                  ></div>
                                </div>
                              </div>
                              <div className="ml-2 w-16 text-right">{(score * 100).toFixed(1)}%</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel; 