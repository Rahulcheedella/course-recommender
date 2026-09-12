import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Chatbot from './components/Chatbot';
import Home from './pages/Home';
import Explore from './pages/Explore';
import CourseDetails from './pages/CourseDetails';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import Wishlist from './pages/Wishlist';
import MyLearning from './pages/MyLearning';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import LearningPathPage from './pages/LearningPathPage';

export default function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/explore" element={<Explore />} />
            <Route path="/course/:id" element={<CourseDetails />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/wishlist" element={<Wishlist />} />
            <Route path="/my-learning" element={<MyLearning />} />
            <Route path="/graph" element={<KnowledgeGraphPage />} />
            <Route path="/learning-path" element={<LearningPathPage />} />
          </Routes>
        </main>

        {/* Global Floating AI Learning Assistant Chatbot */}
        <Chatbot />
      </div>
    </Router>
  );
}
