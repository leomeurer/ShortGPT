import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import AssetLibrary from './pages/AssetLibrary'
import Config from './pages/Config'
import ContentAutomation from './pages/ContentAutomation'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white">
        <Header />
        <main className="container mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/automation" element={<ContentAutomation />} />
            <Route path="/assets" element={<AssetLibrary />} />
            <Route path="/config" element={<Config />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App