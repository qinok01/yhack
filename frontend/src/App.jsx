import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './tailwind.css';
import './index.css';
import PersonalTrainerLanding from './components/PersonalTrainingLanding';
<<<<<<< HEAD
import Fitness from './components/Fitness/Fitness';

const App = () => {
  return (
    <div>
      <Fitness/>
    </div>
=======
import FitnessRoom from './components/FitnessRoom(depreceated)';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<PersonalTrainerLanding />} />
        <Route path="/fitness" element={<FitnessRoom />} />
      </Routes>
    </Router>
>>>>>>> f131c22e673ed8a5943b2b52517e02d2dc6b5f51
  );
};

export default App;
