import React from 'react';
import { Play, Heart, BarChart2, MessageSquare, User, Dumbbell, Watch } from 'lucide-react';
import NavBar from './NavBar';

const PersonalTrainerLanding = () => {
  return (
    <div className="bg-customLightGray min-h-screen w-full flex flex-col mx-auto font-roboto">
      <div className="flex-grow container mx-auto px-4 lg:px-8">
        <NavBar />
        <main className="max-w-6xl mx-auto py-12">
          <div className="flex flex-col lg:flex-row items-center justify-between mb-20">
            <div className="lg:w-1/2 mb-12 lg:mb-0">
            <h1 className="text-5xl font-bold mb-6 leading-tight">
              <span className="text-customeBlue">Your</span> <span className="text-customeBlue italic">Personal Trainer</span>
              <br />
              brought straight to
              <br />
              your living room
            </h1>
              <p className="text-gray-600 text-xl mb-8">Leveraging AI to bring personal PT coach to everyone</p>
              <button className="bg-custom-linear text-white px-8 py-3 rounded-full text-lg font-semibold hover:bg-customeBlue transition duration-300 shadow-lg">
                Start Fitness
              </button>
            </div>
            
            <div className="lg:w-1/2 w-full max-w-md">
              <div className="bg-white p-8 rounded-2xl shadow-2xl">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-2xl font-bold">Fitness Profile</h3>
                  <div className="bg-blue-100 p-2 rounded-full">
                    <User className="text-customeBlue" size={32} />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-6 mb-8">
                  <FitnessIcon Icon={User} label="Profile" />
                  <FitnessIcon Icon={Dumbbell} label="Workouts" />
                  <FitnessIcon Icon={Watch} label="Progress" />
                </div>
                <div className="flex justify-between space-x-4">
                  <button className="flex-1 bg-customeBlue text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-300">
                    Profile
                  </button>
                  <button className="flex-1 bg-gray-200 text-gray-800 py-3 rounded-lg font-semibold hover:bg-gray-300 transition duration-300">
                    Settings
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <section className="pb-6">
            <h2 className="text-3xl font-bold mb-12 text-center">Our Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <FeatureCard 
                title="Realtime Feedback"
                description="Instant Corrections and Support to maximize healthy living"
                Icon={Heart}
                iconColor="text-red-500"
              />
              <FeatureCard 
                title="Video Fitness Plans"
                description="Video walkthroughs of popular fitness routines"
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
                title="Fitness Growth"
                description="Achieve your goals in record time through an interactive fitness workflow"
                Icon={BarChart2}
                iconColor="text-green-500"
              />
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

export default PersonalTrainerLanding;