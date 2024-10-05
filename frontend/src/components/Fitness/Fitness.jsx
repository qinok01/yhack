import React, { useState } from 'react';
import { Maximize2, Minimize2 } from 'lucide-react';
import './Fitness.css';

const VideoPlayer = ({ videoSrc }) => {
  return (
    <video controls className="w-full h-full object-cover">
      <source src={videoSrc} type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  );
};

const WebcamStream = () => {
  return (
    <div className="relative w-full h-full">
      <img 
        src="http://localhost:5001/video_feed"
        className="w-full h-full object-cover"
        alt="Pose Detection Stream"
      />
    </div>
  );
};

const ToggleButton = ({ onClick, isFullScreen }) => {
  return (
    <button
      onClick={onClick}
      className="absolute bottom-4 right-4 p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors"
    >
      {isFullScreen ? <Minimize2 size={24} /> : <Maximize2 size={24} />}
    </button>
  );
};

const Fitness = ({ videoSrc }) => {
  const [view, setView] = useState('split');

  const toggleView = () => {
    if (view === 'split') {
      setView('video');
    } else if (view === 'video') {
      setView('webcam');
    } else {
      setView('split');
    }
  };

  return (
    <div className="w-full h-screen bg-gray-100 relative">
      {view === 'split' && (
        <div className="flex h-full">
          <div className="w-1/2 h-full">
            <VideoPlayer videoSrc={videoSrc} />
          </div>
          <div className="w-1/2 h-full">
            <WebcamStream />
          </div>
        </div>
      )}
      {view === 'video' && (
        <div className="w-full h-full">
          <VideoPlayer videoSrc={videoSrc} />
        </div>
      )}
      {view === 'webcam' && (
        <div className="w-full h-full">
          <WebcamStream />
        </div>
      )}
      <ToggleButton onClick={toggleView} isFullScreen={view !== 'split'} />
    </div>
  );
};

export default Fitness;