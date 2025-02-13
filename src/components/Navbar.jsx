import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/Copy.png';


const Navbar = () => {
    const [user, setUser] = useState(null);

    return (
        <div className="flex items-center justify-between py-4 px-4 sm:px-6 lg:px-10">
            <Link to="/">
                <img src={logo} alt="MediCheck Logo" className="w-30 sm:w-32 lg:w-60" />
            </Link>
            <div>
                {user ? (
                    <div>
                        {/* Render user-related elements here */}
                        <span className="text-gray-800">Welcome, User!</span>
                    </div>
                ) : (
                    <div className="flex items-center gap-2 sm:gap-5">
                        <button className="bg-zinc-800 text-white px-7 py-2 sm:px-10 text-sm rounded-full">
                            Login
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Navbar;
