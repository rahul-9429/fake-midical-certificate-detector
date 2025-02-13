import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Result from './pages/Result';
import Navbar from './components/Navbar';

const App = () => {
  return (
    <div className="px-4 sm:px-8 md:px-12 lg:px-20 xl:px-28 min-h-screen bg-gradient-to-b from-teal-50 to-orange-50">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/result" element={<Result />} />
      </Routes>
    </div>
  );
};

export default App;
