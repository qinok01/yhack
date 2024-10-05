import React from 'react';
import Fivilogo from '../assets/fivi-logo.png'; // Adjust the path to your image

const NavBar = () => {
  return (
    <nav className="p-4 ">
      <div className="container mx-auto flex justify-between items-center ">
        {/* Logo Section */}
        <div>
          <img src={Fivilogo} alt="Fision Logo" className="h-16 w-auto" />
        </div>

        {/* Button Section */}
        <div>
          <button className="bg-custom-linear hover:bg-blue-700 text-white py-2 px-2 rounded-xl font-afacad">
            Try it out
          </button>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
