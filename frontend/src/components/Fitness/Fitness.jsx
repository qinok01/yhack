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
    icon: '/squat icon.png' 
  },
  { 
    id: 2, 
    processed: '/processed_f_fivi_pushups.mp4', 
    unprocessed: '/f_fivi_pushups.mp4', 
    label: 'Pushups',
    icon: '/pushup icon.png' 
  },
  { 
    id: 3, 
    processed: '/processed_f_fivi_plank.mp4', 
    unprocessed: '/f_fivi_plank.mp4', 
    label: 'Plank',
    icon: '/plank icon.png' 
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
  
      // Get the label of the selected exercise
      const selectedExercise = videos[index].label;
  
      // Send a request to the backend to update the current exercise
      fetch('http://localhost:5005/current_exercise', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ exercise: selectedExercise }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to update current exercise');
          }
          return response.json();
        })
        .then((data) => {
          console.log('Exercise updated on backend:', data);
  
          setTimeout(() => {
            setCurrentVideoIndex(index);
            setFadingTo(null);
          }, 330);
        })
        .catch((error) => {
          console.error('Error updating current exercise:', error);
          // Optionally handle the error, e.g., show a message to the user
          setTimeout(() => {
            setCurrentVideoIndex(index);
            setFadingTo(null);
          }, 330);
        });
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
            <img 
              src={video.icon} 
              alt={`${video.label} icon`} 
              className={`icon ${index === currentVideoIndex ? 'active' : ''}`}
            />
          </button>
        ))}
      </div>
      <button onClick={toggleProcessing} className="processing-toggle" disabled={isTransitioning}>
        <Repeat size={24} />
      </button>
    </div>
  );
};

const WebcamStream = ({ isVisible, viewMode }) => {
  return (
    <div className={`webcam-stream ${isVisible ? '' : 'hidden'}`}>
      <img 
        src={`http://localhost:5001/video_feed/${viewMode}`}
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