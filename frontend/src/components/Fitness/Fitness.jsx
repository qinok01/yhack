import React, { useState, useRef, useEffect } from 'react';
import { Maximize2, Minimize2, Home, Repeat } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Fitness.css';

const videos = [
  { 
    id: 1, 
    processed: '/processed_f_fivi_side_squats.mp4', 
    unprocessed: '/f_fivi_side_squats.mp4', 
    label: 'Squats',
    icon: (
      <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" strokeWidth="2" fill="none">
        <path d="M7 17L12 22L17 17" />
        <path d="M12 22L12 10" />
        <circle cx="12" cy="6" r="4" />
      </svg>
    )
  },
  { 
    id: 2, 
    processed: '/processed_f_fivi_pushups.mp4', 
    unprocessed: '/f_fivi_pushups.mp4', 
    label: 'Pushups',
    icon: (
      <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" strokeWidth="2" fill="none">
        <path d="M4 18L20 18" />
        <path d="M5 14L19 14" />
        <circle cx="8" cy="9" r="3" />
        <circle cx="16" cy="9" r="3" />
      </svg>
    )
  },
  { 
    id: 3, 
    processed: '/processed_f_fivi_plank.mp4', 
    unprocessed: '/f_fivi_plank.mp4', 
    label: 'Plank',
    icon: (
      <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" strokeWidth="2" fill="none">
        <path d="M3 12H21" />
        <path d="M6 7V17" />
        <path d="M18 7V17" />
      </svg>
    )
  },
];

const ExercisePlayer = ({ isVisible }) => {
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [fadingTo, setFadingTo] = useState(null);
  const [isProcessed, setIsProcessed] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const videoRefs = useRef(videos.map(() => ({
    processed: React.createRef(),
    unprocessed: React.createRef()
  })));

  useEffect(() => {
    if (isVisible) {
      const currentVideo = videoRefs.current[currentVideoIndex][isProcessed ? 'processed' : 'unprocessed'].current;
      currentVideo.play().catch(error => {
        console.error("Error attempting to play video:", error);
      });
    }
  }, [isVisible, currentVideoIndex, isProcessed]);

  const handleVideoEnd = () => {
    setFadingTo((currentVideoIndex + 1) % videos.length);
    setTimeout(() => {
      setCurrentVideoIndex((currentVideoIndex + 1) % videos.length);
      setFadingTo(null);
    }, 330);
  };

  const switchVideo = (index) => {
    if (index !== currentVideoIndex) {
      setFadingTo(index);
      setTimeout(() => {
        setCurrentVideoIndex(index);
        setFadingTo(null);
      }, 330);
    }
  };

  const toggleProcessing = () => {
    setIsTransitioning(true);
    const currentVideo = videoRefs.current[currentVideoIndex][isProcessed ? 'processed' : 'unprocessed'].current;
    const targetVideo = videoRefs.current[currentVideoIndex][!isProcessed ? 'processed' : 'unprocessed'].current;
    
    targetVideo.currentTime = currentVideo.currentTime;
    targetVideo.play().then(() => {
      setIsProcessed(!isProcessed);
      setTimeout(() => {
        setIsTransitioning(false);
      }, 330);
    }).catch(error => {
      console.error("Error playing target video:", error);
      setIsTransitioning(false);
    });
  };

  return (
    <div className={`exercise-player ${isVisible ? '' : 'hidden'}`}>
      {videos.map((video, index) => (
        <React.Fragment key={video.id}>
          <video
            ref={videoRefs.current[index].processed}
            src={video.processed}
            className={`exercise-video ${isProcessed ? 'active' : ''} ${index === currentVideoIndex ? 'current' : ''} ${fadingTo === index ? 'fading-in' : ''} ${fadingTo !== null && index === currentVideoIndex ? 'fading-out' : ''} ${isTransitioning && isProcessed ? 'fading-out' : ''} ${isTransitioning && !isProcessed ? 'fading-in' : ''}`}
            muted
            loop
            playsInline
            onEnded={handleVideoEnd}
            onError={(e) => console.error("Video error:", e)}
          />
          <video
            ref={videoRefs.current[index].unprocessed}
            src={video.unprocessed}
            className={`exercise-video ${!isProcessed ? 'active' : ''} ${index === currentVideoIndex ? 'current' : ''} ${fadingTo === index ? 'fading-in' : ''} ${fadingTo !== null && index === currentVideoIndex ? 'fading-out' : ''} ${isTransitioning && !isProcessed ? 'fading-out' : ''} ${isTransitioning && isProcessed ? 'fading-in' : ''}`}
            muted
            loop
            playsInline
            onEnded={handleVideoEnd}
            onError={(e) => console.error("Video error:", e)}
          />
        </React.Fragment>
      ))}
      <div className="video-controls">
        {videos.map((video, index) => (
          <button
            key={video.id}
            className={`video-button ${index === currentVideoIndex ? 'active' : ''}`}
            onClick={() => switchVideo(index)}
            aria-label={video.label}
          >
            {video.icon}
          </button>
        ))}
      </div>
      <button onClick={toggleProcessing} className="processing-toggle" disabled={isTransitioning}>
        <Repeat size={24} />
      </button>
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

const ControlButton = ({ onClick, icon: Icon }) => {
  return (
    <button
      onClick={onClick}
      className="control-button"
    >
      <Icon size={24} />
    </button>
  );
};

const Fitness = () => {
  const [view, setView] = useState('split');
  const [transitioning, setTransitioning] = useState(false);
  const navigate = useNavigate();

  const toggleView = () => {
    setTransitioning(true);
    setTimeout(() => {
      if (view === 'split') {
        setView('video');
      } else if (view === 'video') {
        setView('webcam');
      } else {
        setView('split');
      }
      setTransitioning(false);
    }, 330);
  };

  const goHome = () => {
    navigate('/');
  };

  const isVideoVisible = view === 'split' || view === 'video';
  const isWebcamVisible = view === 'split' || view === 'webcam';

  return (
    <div className={`fitness-container ${transitioning ? 'transitioning' : ''}`}>
      <div className={`content ${view}`}>
        <ExercisePlayer isVisible={isVideoVisible} />
        <WebcamStream isVisible={isWebcamVisible} />
      </div>
      <div className="control-buttons">
        <ControlButton onClick={goHome} icon={Home} />
        <ControlButton onClick={toggleView} icon={view !== 'split' ? Maximize2 : Minimize2} />
      </div>
    </div>
  );
};

export default Fitness;