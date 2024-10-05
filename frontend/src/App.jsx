import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './tailwind.css';
import './index.css';
import PersonalTrainerLanding from './components/PersonalTrainingLanding';
import Fitness from './components/Fitness/Fitness';


const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<PersonalTrainerLanding />} />
        <Route path="/fitness" element={<Fitness />} />
      </Routes>
    </Router>
  );
};

export default App;
