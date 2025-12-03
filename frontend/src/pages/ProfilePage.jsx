import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/useAuthStore';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { authUser, logout } = useAuthStore();
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    fullName: authUser?.fullName || '',
    email: authUser?.email || '',
    profilePic: authUser?.profilePic || ''
  });
  const [activeTab, setActiveTab] = useState('account'); // account, preferences, security
  const fileInputRef = useRef(null);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleSave = () => {
    // TODO: Implement profile update API call
    console.log('Saving profile:', formData);
    setIsEditing(false);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setFormData({ ...formData, profilePic: event.target.result });
      };
      reader.readAsDataURL(file);
    }
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
    <div className={`min-h-screen ${bgColor} font-['system-ui',-apple-system,'Segoe_UI',sans-serif] transition-colors`}>
      {/* Header */}
      <header className={`${secondaryBg} border-b ${borderColor} px-4 py-2.5 transition-colors`}>
        <div className="flex items-center justify-between max-w-[2000px] mx-auto">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate('/')}
              className={`p-2 rounded-lg ${hoverBg}`}
            >
              <svg className={`w-6 h-6 ${textColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>

            <button className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${hoverBg} ${textColor}`}>
              <span className="text-sm font-medium">GeoNLI</span>
            </button>
          </div>

          <div className="flex items-center gap-1">
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

            <button
              onClick={handleLogout}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg ${hoverBg} ${textColor}`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="text-sm">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto p-6">
        {/* Profile Header */}
        <div className={`${secondaryBg} border ${borderColor} rounded-xl p-8 mb-6`}>
          <div className="flex items-start gap-6">
            <div className="relative">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-3xl font-semibold">
                {formData.profilePic ? (
                  <img src={formData.profilePic} alt="Profile" className="w-24 h-24 rounded-full object-cover" />
                ) : (
                  authUser?.fullName?.charAt(0)?.toUpperCase() || 'U'
                )}
              </div>
              {isEditing && (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className={`absolute bottom-0 right-0 p-2 ${isDarkMode ? 'bg-white text-black' : 'bg-black text-white'} rounded-full shadow-lg hover:scale-110 transition-transform`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </div>

            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h1 className={`text-2xl font-semibold ${textColor}`}>
                  {authUser?.fullName || 'User'}
                </h1>
                {!isEditing ? (
                  <button
                    onClick={() => setIsEditing(true)}
                    className={`px-4 py-2 ${isDarkMode ? 'bg-white text-black hover:bg-gray-200' : 'bg-black text-white hover:bg-gray-800'} rounded-lg text-sm font-medium transition-colors flex items-center gap-2`}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Edit Profile
                  </button>
                ) : (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setIsEditing(false)}
                      className={`px-4 py-2 ${tertiaryBg} ${textColor} rounded-lg text-sm font-medium ${hoverBg} transition-colors`}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSave}
                      className={`px-4 py-2 ${isDarkMode ? 'bg-white text-black hover:bg-gray-200' : 'bg-black text-white hover:bg-gray-800'} rounded-lg text-sm font-medium transition-colors`}
                    >
                      Save Changes
                    </button>
                  </div>
                )}
              </div>
              <p className={`${secondaryText} text-sm mb-4`}>{authUser?.email}</p>
              <div className="flex items-center gap-4">
                <div className={`px-3 py-1 ${tertiaryBg} rounded-lg`}>
                  <span className={`text-xs ${secondaryText}`}>Plan: </span>
                  <span className={`text-xs ${textColor} font-medium`}>Free</span>
                </div>
                <div className={`px-3 py-1 ${tertiaryBg} rounded-lg`}>
                  <span className={`text-xs ${secondaryText}`}>Member since: </span>
                  <span className={`text-xs ${textColor} font-medium`}>
                    {new Date(authUser?.createdAt || Date.now()).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className={`${secondaryBg} border ${borderColor} rounded-xl overflow-hidden`}>
          <div className={`flex border-b ${borderColor}`}>
            <button
              onClick={() => setActiveTab('account')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'account'
                  ? isDarkMode ? 'bg-[#2f2f2f] text-white border-b-2 border-white' : 'bg-gray-200 text-gray-900 border-b-2 border-black'
                  : `${textColor} ${hoverBg}`
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Account
              </div>
            </button>
            <button
              onClick={() => setActiveTab('preferences')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'preferences'
                  ? isDarkMode ? 'bg-[#2f2f2f] text-white border-b-2 border-white' : 'bg-gray-200 text-gray-900 border-b-2 border-black'
                  : `${textColor} ${hoverBg}`
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
                Preferences
              </div>
            </button>
            <button
              onClick={() => setActiveTab('security')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'security'
                  ? isDarkMode ? 'bg-[#2f2f2f] text-white border-b-2 border-white' : 'bg-gray-200 text-gray-900 border-b-2 border-black'
                  : `${textColor} ${hoverBg}`
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                Security
              </div>
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'account' && (
              <div className="space-y-6">
                <div>
                  <h3 className={`text-lg font-semibold ${textColor} mb-4`}>Account Information</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className={`block text-sm font-medium ${textColor} mb-2`}>
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={formData.fullName}
                        onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                        disabled={!isEditing}
                        className={`w-full px-4 py-3 ${inputBg} ${textColor} border ${borderColor} rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${!isEditing && 'opacity-60 cursor-not-allowed'}`}
                      />
                    </div>

                    <div>
                      <label className={`block text-sm font-medium ${textColor} mb-2`}>
                        Email
                      </label>
                      <input
                        type="email"
                        value={formData.email}
                        disabled
                        className={`w-full px-4 py-3 ${inputBg} ${textColor} border ${borderColor} rounded-lg text-sm opacity-60 cursor-not-allowed`}
                      />
                      <p className={`text-xs ${secondaryText} mt-1`}>
                        Email cannot be changed
                      </p>
                    </div>
                  </div>
                </div>

                <div className={`border-t ${borderColor} pt-6`}>
                  <h3 className={`text-lg font-semibold ${textColor} mb-4`}>Account Stats</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className={`${tertiaryBg} rounded-lg p-4`}>
                      <div className={`text-2xl font-bold ${textColor} mb-1`}>0</div>
                      <div className={`text-xs ${secondaryText}`}>Total Sessions</div>
                    </div>
                    <div className={`${tertiaryBg} rounded-lg p-4`}>
                      <div className={`text-2xl font-bold ${textColor} mb-1`}>0</div>
                      <div className={`text-xs ${secondaryText}`}>Images Analyzed</div>
                    </div>
                    <div className={`${tertiaryBg} rounded-lg p-4`}>
                      <div className={`text-2xl font-bold ${textColor} mb-1`}>0</div>
                      <div className={`text-xs ${secondaryText}`}>API Calls</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'preferences' && (
              <div className="space-y-6">
                <div>
                  <h3 className={`text-lg font-semibold ${textColor} mb-4`}>Display Preferences</h3>
                  
                  <div className="space-y-4">
                    <div className={`flex items-center justify-between p-4 ${tertiaryBg} rounded-lg`}>
                      <div>
                        <div className={`text-sm font-medium ${textColor} mb-1`}>Dark Mode</div>
                        <div className={`text-xs ${secondaryText}`}>Use dark theme across the app</div>
                      </div>
                      <button
                        onClick={() => setIsDarkMode(!isDarkMode)}
                        className={`relative w-12 h-6 rounded-full transition-colors ${isDarkMode ? 'bg-blue-500' : 'bg-gray-300'}`}
                      >
                        <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${isDarkMode ? 'translate-x-6' : ''}`} />
                      </button>
                    </div>

                    <div className={`flex items-center justify-between p-4 ${tertiaryBg} rounded-lg`}>
                      <div>
                        <div className={`text-sm font-medium ${textColor} mb-1`}>Notifications</div>
                        <div className={`text-xs ${secondaryText}`}>Receive email notifications</div>
                      </div>
                      <button className={`relative w-12 h-6 rounded-full transition-colors bg-gray-300`}>
                        <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform`} />
                      </button>
                    </div>

                    <div className={`flex items-center justify-between p-4 ${tertiaryBg} rounded-lg`}>
                      <div>
                        <div className={`text-sm font-medium ${textColor} mb-1`}>Auto-save Sessions</div>
                        <div className={`text-xs ${secondaryText}`}>Automatically save your work</div>
                      </div>
                      <button className={`relative w-12 h-6 rounded-full transition-colors bg-blue-500`}>
                        <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform translate-x-6`} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <div>
                  <h3 className={`text-lg font-semibold ${textColor} mb-4`}>Password & Security</h3>
                  
                  <div className="space-y-4">
                    <button className={`w-full text-left p-4 ${tertiaryBg} rounded-lg ${hoverBg} transition-colors`}>
                      <div className="flex items-center justify-between">
                        <div>
                          <div className={`text-sm font-medium ${textColor} mb-1`}>Change Password</div>
                          <div className={`text-xs ${secondaryText}`}>Update your password</div>
                        </div>
                        <svg className={`w-5 h-5 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </button>

                    <button className={`w-full text-left p-4 ${tertiaryBg} rounded-lg ${hoverBg} transition-colors`}>
                      <div className="flex items-center justify-between">
                        <div>
                          <div className={`text-sm font-medium ${textColor} mb-1`}>Two-Factor Authentication</div>
                          <div className={`text-xs ${secondaryText}`}>Add an extra layer of security</div>
                        </div>
                        <span className={`text-xs px-2 py-1 ${isDarkMode ? 'bg-yellow-500/20 text-yellow-500' : 'bg-yellow-100 text-yellow-700'} rounded`}>
                          Coming Soon
                        </span>
                      </div>
                    </button>

                    <button className={`w-full text-left p-4 ${tertiaryBg} rounded-lg ${hoverBg} transition-colors`}>
                      <div className="flex items-center justify-between">
                        <div>
                          <div className={`text-sm font-medium ${textColor} mb-1`}>Active Sessions</div>
                          <div className={`text-xs ${secondaryText}`}>Manage your logged-in devices</div>
                        </div>
                        <svg className={`w-5 h-5 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </button>
                  </div>
                </div>

                <div className={`border-t ${borderColor} pt-6`}>
                  <h3 className={`text-lg font-semibold text-red-500 mb-4`}>Danger Zone</h3>
                  
                  <button className={`w-full text-left p-4 border-2 border-red-500/20 rounded-lg hover:border-red-500/40 transition-colors`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className={`text-sm font-medium text-red-500 mb-1`}>Delete Account</div>
                        <div className={`text-xs ${secondaryText}`}>Permanently delete your account and all data</div>
                      </div>
                      <svg className={`w-5 h-5 text-red-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}