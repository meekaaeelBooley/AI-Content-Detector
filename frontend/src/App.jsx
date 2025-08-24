// Main application component that serves as the root container
import AITextDetectorPage from './features/AITextDetectorPage/AITextDetectorPage'
import './App.css'

function App() {
  return (
    <div className="App">
      {/* Renders the main AI text detector page component */}
      <AITextDetectorPage />
    </div>
  )
}

export default App