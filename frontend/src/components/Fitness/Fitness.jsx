import React, { useState, useRef, useEffect } from 'react';
import { Maximize2, Minimize2 } from 'lucide-react';
import './Fitness.css';

const VideoPlayer = ({ isVisible }) => {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current) {
      if (isVisible) {
        videoRef.current.play().catch(error => {
          console.error("Error attempting to play video:", error);
        });
      } else {
        videoRef.current.pause();
      }
    }
  }, [isVisible]);

  return (
    <div className={`video-player ${isVisible ? '' : 'hidden'}`}>
      <video
        ref={videoRef}
        src="/fitness_video.mp4"
        muted
        loop
        playsInline
      />
    </div>
  );
};

const WebcamStream = ({ isVisible }) => {
  return (
    <div className={`webcam-stream ${isVisible ? '' : 'hidden'}`}>
      <img 
        src="http://localhost:5001/video_feed"
        alt="Pose Detection Stream"
      />
    </div>
  );
};

const ToggleButton = ({ onClick, isFullScreen }) => {
  return (
    <button
      onClick={onClick}
      className="toggle-button"
    >
      {isFullScreen ? <Minimize2 size={24} /> : <Maximize2 size={24} />}
    </button>
  );
};

const Fitness = () => {
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

  const isVideoVisible = view === 'split' || view === 'video';
  const isWebcamVisible = view === 'split' || view === 'webcam';

  return (
    <div className="fitness-container">
      <div className={`content ${view}`}>
        <VideoPlayer isVisible={isVideoVisible} />
        <WebcamStream isVisible={isWebcamVisible} />
      </div>
      <ToggleButton onClick={toggleView} isFullScreen={view !== 'split'} />
    </div>
  );
};

export default Fitness;