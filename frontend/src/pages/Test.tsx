import React from 'react'

const Test: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Tailwind CSS Test</h1>
        <p className="text-gray-600 mb-6">
          If you can see this styled card with gradients and shadows, Tailwind CSS is working correctly!
        </p>
        <div className="space-y-4">
          <button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition-colors">
            Primary Button
          </button>
          <button className="w-full bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-md transition-colors">
            Success Button
          </button>
          <button className="w-full bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-md transition-colors">
            Danger Button
          </button>
        </div>
        <div className="mt-6 p-4 bg-gray-100 rounded-md">
          <h3 className="font-medium text-gray-900 mb-2">Grid Test</h3>
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-blue-200 h-8 rounded"></div>
            <div className="bg-green-200 h-8 rounded"></div>
            <div className="bg-red-200 h-8 rounded"></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Test