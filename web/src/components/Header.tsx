import { Link, useLocation } from 'react-router-dom'

const Header = () => {
  const location = useLocation()
  
  const navigation = [
    { name: 'Dashboard', path: '/' },
    { name: 'Content Automation', path: '/automation' },
    { name: 'Asset Library', path: '/assets' },
    { name: 'Config', path: '/config' },
  ]

  const isActive = (path: string) => {
    return location.pathname === path
  }

  return (
    <header className="border-b border-gray-200">
      <div className="container mx-auto px-4">
        {/* Top bar with title and buttons */}
        <div className="flex justify-between items-center py-2">
          <h1 className="text-4xl font-bold text-gray-900">ShortGPT</h1>
          
          <div className="flex space-x-3">
            <a 
              href="https://discord.gg/bWreuAyRaj" 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-5 py-2 text-white bg-[#7289DA] hover:bg-[#5b6eae] rounded-md font-medium transition-colors"
            >
              Join Discord
            </a>
            <a 
              href="https://github.com/RayVentura/ShortGPT" 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-5 py-2 text-white bg-gray-800 hover:bg-gray-700 rounded-md font-medium transition-colors"
            >
              Like the concept? Add a Star on Github 👉 ⭐
            </a>
          </div>
        </div>

        {/* Navigation tabs */}
        <nav className="flex space-x-1">
          {navigation.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`px-4 py-3 text-sm font-medium rounded-t-md border-b-2 transition-colors ${
                isActive(item.path)
                  ? 'bg-blue-50 text-blue-700 border-blue-500'
                  : 'text-gray-600 hover:text-gray-900 border-transparent hover:border-gray-300'
              }`}
            >
              {item.name}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  )
}

export default Header