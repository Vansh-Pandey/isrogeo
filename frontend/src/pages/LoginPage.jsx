import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/useAuthStore';

export default function LoginPage() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: ''
  });

  const { login, signup, isLogging, isRegistering } = useAuthStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (isLogin) {
      const success = await login({
        email: formData.email,
        password: formData.password
      });
      if (success) {
        navigate('/');
      }
    } else {
      if (!formData.fullName.trim()) {
        return;
      }
      const success = await signup({
        email: formData.email,
        password: formData.password,
        fullName: formData.fullName
      });
      if (success) {
        navigate('/');
      }
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const bgColor = isDarkMode ? 'bg-[#212121]' : 'bg-white';
  const secondaryBg = isDarkMode ? 'bg-[#171717]' : 'bg-gray-50';
  const tertiaryBg = isDarkMode ? 'bg-[#2f2f2f]' : 'bg-gray-100';
  const borderColor = isDarkMode ? 'border-[#3d3d3d]' : 'border-gray-200';
  const textColor = isDarkMode ? 'text-[#ececec]' : 'text-gray-900';
  const secondaryText = isDarkMode ? 'text-[#b4b4b4]' : 'text-gray-600';
  const hoverBg = isDarkMode ? 'hover:bg-[#2f2f2f]' : 'hover:bg-gray-100';
  const inputBg = isDarkMode ? 'bg-[#2f2f2f]' : 'bg-white';

  return (
    <div className={`min-h-screen ${bgColor} font-['system-ui',-apple-system,'Segoe_UI',sans-serif] transition-colors flex flex-col`}>
      {/* Header */}
      <header className={`${secondaryBg} border-b ${borderColor} px-4 py-2.5 transition-colors`}>
        <div className="flex items-center justify-between max-w-[2000px] mx-auto">
          <div className="flex items-center gap-3">
            <button className={`p-2 rounded-lg ${hoverBg}`}>
              <svg className={`w-6 h-6 ${textColor}`} fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
              </svg>
            </button>
            
            <div className="flex items-center gap-2">
              <span className={`text-sm font-medium ${textColor}`}>GeoNLI</span>
            </div>
          </div>
          
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className={`p-2 rounded-lg ${hoverBg} transition-colors`}
            title={isDarkMode ? 'Light mode' : 'Dark mode'}
          >
            {isDarkMode ? (
              <svg className={`w-5 h-5 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg className={`w-5 h-5 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Logo Section */}
          <div className="text-center mb-8">
            <div className="inline-block mb-4">
              <div className={`w-16 h-16 ${isDarkMode ? 'bg-white' : 'bg-black'} rounded-2xl flex items-center justify-center`}>
                <svg className={`w-10 h-10 ${isDarkMode ? 'text-black' : 'text-white'}`} fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                  <path d="M13 7h-2v5h5v-2h-3z"/>
                </svg>
              </div>
            </div>
            <h1 className={`text-2xl font-semibold ${textColor} mb-2`}>
              {isLogin ? 'Welcome back' : 'Create your account'}
            </h1>
            <p className={`text-sm ${secondaryText}`}>
              {isLogin 
                ? 'Enter your credentials to access your account' 
                : 'Get started with satellite image analysis'}
            </p>
          </div>

          {/* Auth Form */}
          <div className={`${secondaryBg} border ${borderColor} rounded-xl p-8`}>
            {/* Toggle Tabs */}
            <div className={`flex ${tertiaryBg} rounded-lg p-1 mb-6`}>
              <button
                onClick={() => setIsLogin(true)}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
                  isLogin 
                    ? isDarkMode ? 'bg-white text-black' : 'bg-black text-white'
                    : `${textColor} ${hoverBg}`
                }`}
              >
                Login
              </button>
              <button
                onClick={() => setIsLogin(false)}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
                  !isLogin 
                    ? isDarkMode ? 'bg-white text-black' : 'bg-black text-white'
                    : `${textColor} ${hoverBg}`
                }`}
              >
                Sign Up
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Full Name (only for signup) */}
              {!isLogin && (
                <div>
                  <label className={`block text-sm font-medium ${textColor} mb-2`}>
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    required={!isLogin}
                    placeholder="John Doe"
                    className={`w-full px-4 py-3 ${inputBg} ${textColor} border ${borderColor} rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all`}
                  />
                </div>
              )}

              {/* Email */}
              <div>
                <label className={`block text-sm font-medium ${textColor} mb-2`}>
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="you@example.com"
                  className={`w-full px-4 py-3 ${inputBg} ${textColor} border ${borderColor} rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all`}
                />
              </div>

              {/* Password */}
              <div>
                <label className={`block text-sm font-medium ${textColor} mb-2`}>
                  Password
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  placeholder="••••••••"
                  minLength={6}
                  className={`w-full px-4 py-3 ${inputBg} ${textColor} border ${borderColor} rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all`}
                />
                {!isLogin && (
                  <p className={`text-xs ${secondaryText} mt-1`}>
                    Must be at least 6 characters
                  </p>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLogging || isRegistering}
                className={`w-full py-3 ${isDarkMode ? 'bg-white text-black hover:bg-gray-100' : 'bg-black text-white hover:bg-gray-800'} rounded-lg font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
              >
                {(isLogging || isRegistering) ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {isLogin ? 'Logging in...' : 'Creating account...'}
                  </>
                ) : (
                  <>
                    {isLogin ? 'Login' : 'Create Account'}
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className={`absolute inset-0 flex items-center`}>
                <div className={`w-full border-t ${borderColor}`}></div>
              </div>
              <div className="relative flex justify-center text-xs">
                <span className={`px-2 ${secondaryBg} ${secondaryText}`}>
                  {isLogin ? 'New to GeoNLI?' : 'Already have an account?'}
                </span>
              </div>
            </div>

            {/* Switch Auth Mode */}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className={`w-full text-center text-sm ${secondaryText} hover:${textColor} transition-colors`}
            >
              {isLogin ? (
                <>
                  Don't have an account? <span className="font-medium">Sign up</span>
                </>
              ) : (
                <>
                  Already have an account? <span className="font-medium">Login</span>
                </>
              )}
            </button>
          </div>

          {/* Footer */}
          <p className={`text-center text-xs ${secondaryText} mt-8`}>
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}