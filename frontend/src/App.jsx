// Main application component that serves as the root container
import { Routes, Route } from 'react-router-dom';
import HomePage from './features/HomePage/HomePage';
import AITextDetectorPage from './features/AITextDetectorPage/AITextDetectorPage';
import './App.css';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/AITextDetectorPage" element={<AITextDetectorPage />} />
      </Routes>
    </div>
  );
}

export default App;