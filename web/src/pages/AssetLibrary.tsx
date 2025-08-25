const AssetLibrary = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Asset Library</h2>
          <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors">
            + Add Asset
          </button>
        </div>
        
        <div className="border rounded-lg p-4">
          <p className="text-gray-600 text-center py-8">
            Asset management interface coming soon...
          </p>
          <p className="text-sm text-gray-500 text-center">
            This will include file upload, asset preview, and management features.
          </p>
        </div>
      </div>
    </div>
  )
}

export default AssetLibrary