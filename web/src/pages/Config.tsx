import { useState, useEffect } from 'react'
import axios from 'axios'

interface ApiKeys {
  OPENAI_API_KEY: string
  ELEVENLABS_API_KEY: string
  PEXELS_API_KEY: string
  GEMINI_API_KEY: string
  GROQ_API_KEY: string
}

interface ApiKeyFieldProps {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  showCharacters?: boolean
  charactersRemaining?: string
}

const ApiKeyField = ({ label, value, onChange, placeholder, showCharacters, charactersRemaining }: ApiKeyFieldProps) => {
  const [isVisible, setIsVisible] = useState(false)
  
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      <div className="flex gap-2">
        <input
          type={isVisible ? "text" : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          type="button"
          onClick={() => setIsVisible(!isVisible)}
          className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-md transition-colors"
        >
          {isVisible ? 'Hide' : 'Show'}
        </button>
      </div>
      {showCharacters && charactersRemaining && (
        <div className="text-sm text-gray-600">
          Characters remaining: {charactersRemaining}
        </div>
      )}
    </div>
  )
}

const Config = () => {
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    OPENAI_API_KEY: '',
    ELEVENLABS_API_KEY: '',
    PEXELS_API_KEY: '',
    GEMINI_API_KEY: '',
    GROQ_API_KEY: ''
  })
  const [elevenCharacters, setElevenCharacters] = useState('')
  const [loading, setLoading] = useState(false)
  const [saveStatus, setSaveStatus] = useState('')

  // Load current API keys on mount
  useEffect(() => {
    loadApiKeys()
  }, [])

  const loadApiKeys = async () => {
    try {
      const response = await axios.get('/api/config/keys')
      setApiKeys(response.data)
      if (response.data.ELEVENLABS_API_KEY) {
        checkElevenLabsCharacters(response.data.ELEVENLABS_API_KEY)
      }
    } catch (error) {
      console.error('Failed to load API keys:', error)
    }
  }

  const checkElevenLabsCharacters = async (apiKey: string) => {
    if (!apiKey) return
    try {
      const response = await axios.post('/api/config/elevenlabs/verify', { api_key: apiKey })
      setElevenCharacters(response.data.characters_remaining)
    } catch (error) {
      setElevenCharacters('Error verifying key')
    }
  }

  const handleKeyChange = (key: keyof ApiKeys, value: string) => {
    setApiKeys(prev => ({ ...prev, [key]: value }))
    if (key === 'ELEVENLABS_API_KEY') {
      checkElevenLabsCharacters(value)
    }
  }

  const saveKeys = async () => {
    setLoading(true)
    setSaveStatus('')
    try {
      await axios.post('/api/config/keys', apiKeys)
      setSaveStatus('Keys Saved!')
      setTimeout(() => setSaveStatus(''), 3000)
    } catch (error) {
      setSaveStatus('Error saving keys')
      console.error('Failed to save API keys:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">API Configuration</h2>
        
        <div className="space-y-6 max-w-2xl">
          <ApiKeyField
            label="OpenAI API Key"
            value={apiKeys.OPENAI_API_KEY}
            onChange={(value) => handleKeyChange('OPENAI_API_KEY', value)}
            placeholder="sk-..."
          />

          <ApiKeyField
            label="ElevenLabs API Key"
            value={apiKeys.ELEVENLABS_API_KEY}
            onChange={(value) => handleKeyChange('ELEVENLABS_API_KEY', value)}
            placeholder="Enter your ElevenLabs API key"
            showCharacters={true}
            charactersRemaining={elevenCharacters}
          />

          <ApiKeyField
            label="Pexels API Key"
            value={apiKeys.PEXELS_API_KEY}
            onChange={(value) => handleKeyChange('PEXELS_API_KEY', value)}
            placeholder="Enter your Pexels API key"
          />

          <ApiKeyField
            label="Gemini API Key"
            value={apiKeys.GEMINI_API_KEY}
            onChange={(value) => handleKeyChange('GEMINI_API_KEY', value)}
            placeholder="Enter your Gemini API key"
          />

          <ApiKeyField
            label="Groq API Key"
            value={apiKeys.GROQ_API_KEY}
            onChange={(value) => handleKeyChange('GROQ_API_KEY', value)}
            placeholder="Enter your Groq API key"
          />

          <div className="flex items-center gap-4">
            <button
              onClick={saveKeys}
              disabled={loading}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                loading
                  ? 'bg-gray-400 text-white cursor-not-allowed'
                  : saveStatus === 'Keys Saved!'
                  ? 'bg-green-600 text-white'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {loading ? 'Saving...' : saveStatus || 'Save'}
            </button>
            
            {saveStatus && (
              <span className={`text-sm ${
                saveStatus === 'Keys Saved!' ? 'text-green-600' : 'text-red-600'
              }`}>
                {saveStatus}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuration Help</h3>
        <div className="space-y-3 text-sm text-gray-600">
          <p><strong>OpenAI:</strong> Required for content generation and AI features</p>
          <p><strong>ElevenLabs:</strong> Required for voice synthesis and TTS features</p>
          <p><strong>Pexels:</strong> Required for stock footage and images</p>
          <p><strong>Gemini:</strong> Alternative AI provider for content generation</p>
          <p><strong>Groq:</strong> Fast inference for AI processing</p>
        </div>
      </div>
    </div>
  )
}

export default Config