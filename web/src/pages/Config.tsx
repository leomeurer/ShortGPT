const Config = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Configuration</h2>
        
        <div className="space-y-6">
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-3">API Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  placeholder="sk-..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ElevenLabs API Key
                </label>
                <input
                  type="password"
                  placeholder="Enter your ElevenLabs API key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-3">General Settings</h3>
            <p className="text-gray-600 text-sm">
              Configuration interface coming soon...
            </p>
          </div>
          
          <button className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition-colors">
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  )
}

export default Config