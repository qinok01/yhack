import React from 'react';
import Fivilogo from '../assets/fivi-logo.png'; // Adjust the path to your image
import { Link } from 'react-router-dom';
const NavBar = ({ showButton  = true}) => {
  return (
    <nav className="px-4 py-2">
      <div className="container mx-auto flex justify-between items-center ">
        {/* Logo Section */}
        <Link to="/">
        <div>
          <img src={Fivilogo} alt="Fision Logo" className="h-16 w-auto" />
        </div>
        </Link>

        {/* Button Section */}
        {showButton && (
          <div>
            <Link to="/fitness">
              <button className="bg-custom-linear hover:bg-blue-700 text-white py-2 px-2 rounded-xl font-afacad">
                Try it out
              </button>
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default NavBar;
