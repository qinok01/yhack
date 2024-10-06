import React from 'react';
import { Play, Flame, ChevronsUp, Heart, BarChart2, MessageSquare, User, Dumbbell, Watch } from 'lucide-react';
import NavBar from './NavBar';
import coach from '../assets/coach.png';
import { Link } from 'react-router-dom';

const PersonalTrainerLanding = () => {
  return (
    <div className="bg-customLightGray min-h-screen w-full flex flex-col mx-auto font-roboto">
      <div className="flex-grow container mx-auto">
        <main className="max-w-6xl mx-auto py-2">
        <NavBar />
          <div className="flex flex-col lg:flex-row items-center justify-between mb-20">
            <div className="lg:w-1/2 mb-12 lg:mb-0">
            <h1 className="text-5xl font-bold mb-6 leading-tight">
              <span className="text-customeBlue">Your</span> <span className="text-customeBlue italic">Personal Trainer</span>
              <br />
              brought straight to
              <br />
              your living room
            </h1>
              <p className="text-gray-600 text-xl mb-8">Leveraging AI to bring personal AI Personal Training to everyone</p>
              <Link to="/fitness">
              <button className="bg-custom-linear text-white px-12 py-4 rounded-full text-xl font-semibold hover:bg-customeBlue transition duration-300 shadow-lg mx-auto">
                Start Fitness
              </button>
              </Link>
            </div>
            
            <div className="lg:w-1/2 w-full max-w-md">
              <img src={coach} alt="Personal Trainer" className="w-full rounded-lg" />

            </div>
          

          
          
          
          </div>
          
          <section className="pb-6">
            <h2 className="text-3xl font-bold mb-12 text-center text-customeBlue">Our Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <FeatureCard 
                title="Realtime Feedback"
                description="Instant Corrections and support to encourage healthy habits"
                Icon={Heart}
                iconColor="text-red-500"
              />
              <FeatureCard 
                title="Video Fitness Tutorials"
                description="Video walkthroughs of popular exercises"
                Icon={Play}
                iconColor="text-blue-500"
              />
              <FeatureCard 
                title="Fitness Companion"
                description="Our Computer Vision AI agent will guide and entertain you throughout your workout"
                Icon={MessageSquare}
                iconColor="text-purple-500"
              />
              <FeatureCard 
                title="Steady Growth"
                description="Achieve your goals in record time through an interactive fitness workflow"
                Icon={BarChart2}
                iconColor="text-green-500"
              />
            </div>
          </section>

          <section className="pb-6">
  <div className="flex w-full pt-4">
    <div className="w-1/2 p-4">
      <BreakCard />
    </div>
    <div className="w-1/2 p-4">
      <MotivationalCard />
    </div>
  </div>
</section>


        </main>
      </div>
    </div>
  );
};

const FitnessIcon = ({ Icon, label }) => (
  <div className="flex flex-col items-center">
    <div className="bg-blue-100 p-3 rounded-full mb-2">
      <Icon className="text-blue-600" size={24} />
    </div>
    <span className="text-sm font-medium text-gray-600">{label}</span>
  </div>
);

const FeatureCard = ({ title, description, Icon, iconColor }) => (
  <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition duration-300">
    <Icon className={`${iconColor} mb-4`} size={32} />
    <h3 className="text-xl font-bold mb-2">{title}</h3>
    <p className="text-gray-600">{description}</p>
  </div>
);

const BreakCard = () => {
  return (
    <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-md w-full mx-auto">
      {/* Card Title */}
      <h3 className="text-2xl font-bold mb-4 text-gray-800">Break Into Fitness</h3>

      {/* Daily Motivation */}
      <p className="text-lg italic text-gray-600 mb-6">
        Getting started is the hardest part...<br /> SO LET'S GET STARTED!
      </p>

      {/* Benefits */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <div className="bg-blue-100 p-3 rounded-full">
            <User className="text-customBlue" size={32} />
          </div>
          <div className="ml-4">
            <p className="text-xl font-bold text-gray-800">Real Feedback</p>
            <p className="text-sm text-gray-500">
              Get immediate feedback to improve your form and progress.
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <div className="bg-blue-100 p-3 rounded-full">
            <Dumbbell className="text-green-500" size={32} />
          </div>
          <div className="ml-4">
            <p className="text-xl font-bold text-gray-800">Real Workouts</p>
            <p className="text-sm text-gray-500">
              Follow effective, customized workout plans that fit your goals.
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <div className="bg-blue-100 p-3 rounded-full">
            <Watch className="text-purple-500" size={32} />
          </div>
          <div className="ml-4 ">
            <p className="text-xl font-bold text-gray-800">Real Progress</p>
            <p className="text-sm text-gray-500">
              Track your fitness journey and see real improvements over time.
            </p>
          </div>
        </div>
      </div>

      {/* Start Workout Button */}
      <div className="flex justify-center">
      <Link to="/fitness">

        <button className="bg-blue-600 text-white py-3 px-6 rounded-full font-semibold hover:bg-blue-700 transition duration-300 shadow-lg">
          Start Fitness
        </button>
      </Link>
      </div>
    </div>
  );
};


const MotivationalCard = () => {
  return (
    <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-md w-full mx-auto">
  {/* Card Title */}
  <h3 className="text-2xl font-bold mb-4 text-gray-800">Find Motivation</h3>

  {/* Daily Quote */}
  <p className="text-lg italic text-gray-600 mb-6">
    Bring your fitness goals to the next level... <br /> with an AI Personal Trainer!
  </p>

  {/* Streak Benefits */}
  <div className="flex items-center justify-between mb-8">
    <div className="flex items-center">
      <div className="bg-blue-100 p-3 rounded-full">
        <Flame className="text-red-500" size={32} />
      </div>
      <div className="ml-4">
        <p className="text-xl font-bold text-gray-800">Consistency Builds Habits</p>
        <p className="text-sm text-gray-500">
          Research shows that streaks reinforce commitment and build healthy habits.
        </p>
      </div>
    </div>
  </div>

  <div className="flex items-center justify-between mb-8">
    <div className="flex items-center">
      <div className="bg-blue-100 p-3 rounded-full">
        <ChevronsUp className="text-green-500" size={32} />
      </div>
      <div className="ml-4">
        <p className="text-xl font-bold text-gray-800">Boost Performance</p>
        <p className="text-sm text-gray-500">
          Consistent effort leads to gradual improvement in strength and endurance.
        </p>
      </div>
    </div>
  </div>

  <div className="flex items-center justify-between mb-8">
    <div className="flex items-center">
      <div className="bg-blue-100 p-3 rounded-full">
        <Heart className="text-purple-500" size={32} />
      </div>
      <div className="ml-4">
        <p className="text-xl font-bold text-gray-800">Mental Health Benefits</p>
        <p className="text-sm text-gray-500">
          Physical activity improves mood and reduces stress levels over time.
        </p>
      </div>
    </div>
  </div>

  {/* Start Workout Button */}
  <div className="flex justify-center">
  <Link to="/fitness">
    <button className="bg-blue-600 text-white py-3 px-6 rounded-full font-semibold hover:bg-blue-700 transition duration-300 shadow-lg">
      Start Fitness
    </button>
  </Link>
  </div>
</div>

  );
};








export default PersonalTrainerLanding;