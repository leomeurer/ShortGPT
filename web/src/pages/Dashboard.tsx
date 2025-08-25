const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to ShortGPT</h2>
        <p className="text-gray-600 mb-4">
          Create automated short videos with AI. Choose an option from the navigation to get started.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg mb-2">🎬 Content Automation</h3>
            <p className="text-gray-600 text-sm">
              Automate the creation of shorts, videos with stock assets, and multilingual dubbing.
            </p>
          </div>
          
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg mb-2">📁 Asset Library</h3>
            <p className="text-gray-600 text-sm">
              Manage your videos, audio files, and other assets for content creation.
            </p>
          </div>
          
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg mb-2">⚙️ Configuration</h3>
            <p className="text-gray-600 text-sm">
              Set up your API keys and configure settings for optimal performance.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard