import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './tailwind.css';
import './index.css';
import PersonalTrainerLanding from './components/PersonalTrainingLanding';
import FitnessRoom from './components/FitnessRoom(depreceated)';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<PersonalTrainerLanding />} />
        <Route path="/fitness" element={<FitnessRoom />} />
      </Routes>
    </Router>
  );
};

export default App;
