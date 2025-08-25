const ContentAutomation = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">🏆 Content Automation 🚀</h2>
        <p className="text-gray-600 mb-6">Choose your desired automation task.</p>
        
        <div className="space-y-4">
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">🎬 Automate the creation of shorts</h3>
            <p className="text-gray-600 text-sm mb-3">
              Create engaging short videos automatically with AI-generated content.
            </p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
              Coming Soon
            </button>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">🎞️ Automate a video with stock assets</h3>
            <p className="text-gray-600 text-sm mb-3">
              Generate videos using stock footage and AI-powered content creation.
            </p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
              Coming Soon
            </button>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">🌐 Automate multilingual video dubbing</h3>
            <p className="text-gray-600 text-sm mb-3">
              Translate and dub your videos into multiple languages automatically.
            </p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContentAutomation