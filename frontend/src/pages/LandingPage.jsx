import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/useAuthStore';
import { useSessionStore } from '../stores/useSessionStore';
import { useMessageStore } from '../stores/useMessageStore';
import { useImageStore } from '../stores/useImageStore';
import { useProjectStore } from '../stores/useProjectStore';
import { useUIStore } from '../stores/useUIstore';

export default function LandingPage() {
  const navigate = useNavigate();

  // Auth Store
  const { authUser, logout } = useAuthStore();

  // Session Store
  const {
    sessions,
    activeSession,
    isCreating,
    fetchSessions,
    createSession,
    renameSession,
    archiveSession,
    deleteSession,
    setActiveSession,
    moveToProject,
    shareSession,
  } = useSessionStore();

  // Message Store
  const {
    messages,
    isTyping,
    isSending,
    fetchMessages,
    sendMessage,
    exportChat,
    copyMessage,
    clearMessages,
  } = useMessageStore();

  // Image Store
  const {
    selectedImage,
    fileName,
    imageZoom,
    isUploading,
    setImageFromFile,
    removeImage,
    downloadImage,
    zoomIn,
    zoomOut,
  } = useImageStore();

  // Project Store
  const { projects, fetchProjects } = useProjectStore();

  // UI Store
  const {
    isDarkMode,
    sidebarCollapsed,
    leftWidth,
    rightWidth,
    showSearch,
    searchQuery,
    showArchived,
    showSessionMenu,
    showMoveMenu,
    dragActive,
    toggleDarkMode,
    setSidebarCollapsed,
    setLeftWidth,
    setRightWidth,
    toggleSearch,
    setSearchQuery,
    toggleArchived,
    setShowSessionMenu,
    setShowMoveMenu,
    setDragActive,
  } = useUIStore();

  // Local state
  const [chatMessage, setChatMessage] = useState('');
  const [isResizingLeft, setIsResizingLeft] = useState(false);
  const [isResizingRight, setIsResizingRight] = useState(false);

  // Refs
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);
  const dropZoneRef = useRef(null);
  const searchInputRef = useRef(null);

  // Fetch sessions and projects on mount
  useEffect(() => {
    fetchSessions();
    fetchProjects();
  }, []); // Only run once on mount

  // Fetch messages when active session changes
  useEffect(() => {
    if (activeSession) {
      fetchMessages(activeSession);
    } else {
      clearMessages();
    }
  }, [activeSession]); // Only depend on activeSession

  // Scroll to bottom when messages change
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus search input when opened
  useEffect(() => {
    if (showSearch && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [showSearch]);

  // Handle resizing
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isResizingLeft) {
        setLeftWidth(e.clientX);
      }
      if (isResizingRight) {
        const newWidth = window.innerWidth - e.clientX;
        setRightWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizingLeft(false);
      setIsResizingRight(false);
    };

    if (isResizingLeft || isResizingRight) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizingLeft, isResizingRight, setLeftWidth, setRightWidth]);

  // Handlers with useCallback to prevent recreating functions
  const handleLogout = useCallback(async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  }, [logout, navigate]);

  const handleImageUpload = useCallback((file) => {
    if (file && (file.type === 'image/jpeg' || file.type === 'image/png')) {
      setImageFromFile(file);
    }
  }, [setImageFromFile]);

  const handleFileSelect = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) handleImageUpload(file);
  }, [handleImageUpload]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, [setDragActive]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleImageUpload(file);
  }, [setDragActive, handleImageUpload]);

  const handleChatMessageChange = useCallback((e) => {
    setChatMessage(e.target.value);
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!chatMessage.trim()) return;
    
    // Auto-create session if none exists
    if (!activeSession && !isCreating) {
      try {
        const newSession = await createSession({ 
          name: `New Analysis ${sessions.length + 1}` 
        });
        if (newSession && newSession._id) {
          await sendMessage(newSession._id, chatMessage, selectedImage);
          setChatMessage('');
        }
      } catch (error) {
        console.error('Error creating session and sending message:', error);
      }
      return;
    }

    // Send message to existing session
    if (activeSession) {
      try {
        await sendMessage(activeSession, chatMessage, selectedImage);
        setChatMessage('');
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
  }, [chatMessage, activeSession, isCreating, sessions.length, createSession, sendMessage, selectedImage]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const handleCreateNewSession = useCallback(async () => {
    try {
      await createSession({ name: `New Analysis ${sessions.length + 1}` });
      setShowSessionMenu(null);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  }, [createSession, sessions.length, setShowSessionMenu]);

  const handleDeleteSession = useCallback(async (sessionId) => {
    // Validation
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
      console.error('Invalid session ID:', sessionId);
      return;
    }

    // Confirm deletion
    const session = sessions.find(s => s._id === sessionId);
    if (!session) {
      console.error('Session not found:', sessionId);
      return;
    }

    if (!window.confirm(`Delete "${session.name}"?`)) {
      return;
    }

    try {
      await deleteSession(sessionId);
      setShowSessionMenu(null);
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  }, [sessions, deleteSession, setShowSessionMenu]);

  const handleRenameSession = useCallback(async (sessionId) => {
    if (!sessionId) return;

    const session = sessions.find((s) => s._id === sessionId);
    if (!session) return;

    const newName = prompt('Rename session:', session.name);
    if (newName && newName.trim() && newName !== session.name) {
      try {
        await renameSession(sessionId, newName.trim());
        setShowSessionMenu(null);
      } catch (error) {
        console.error('Error renaming session:', error);
      }
    } else {
      setShowSessionMenu(null);
    }
  }, [sessions, renameSession, setShowSessionMenu]);

  const handleArchiveSession = useCallback(async (sessionId) => {
    if (!sessionId) return;

    try {
      await archiveSession(sessionId);
      setShowSessionMenu(null);
    } catch (error) {
      console.error('Error archiving session:', error);
    }
  }, [archiveSession, setShowSessionMenu]);

  const handleMoveToProject = useCallback(async (sessionId, projectId) => {
    if (!sessionId || !projectId) return;

    try {
      await moveToProject(sessionId, projectId);
      setShowSessionMenu(null);
      setShowMoveMenu(null);
    } catch (error) {
      console.error('Error moving session to project:', error);
    }
  }, [moveToProject, setShowSessionMenu, setShowMoveMenu]);

  const handleShareSession = useCallback(async (sessionId) => {
    if (!sessionId) return;

    try {
      await shareSession(sessionId);
      setShowSessionMenu(null);
    } catch (error) {
      console.error('Error sharing session:', error);
    }
  }, [shareSession, setShowSessionMenu]);

  const handleExportChat = useCallback(() => {
    const session = sessions.find((s) => s._id === activeSession);
    exportChat(session?.name || 'chat');
  }, [sessions, activeSession, exportChat]);

  // Filter sessions - FIXED: Proper filtering logic
  const filteredSessions = sessions.filter((s) => {
    const matchesArchiveFilter = showArchived ? s.archived === true : s.archived !== true;
    const matchesSearchQuery = s.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesArchiveFilter && matchesSearchQuery;
  });

  // Theme colors - FIXED: Complete classes
  const bgColor = isDarkMode ? 'bg-[#212121]' : 'bg-white';
  const secondaryBg = isDarkMode ? 'bg-[#171717]' : 'bg-gray-50';
  const tertiaryBg = isDarkMode ? 'bg-[#2f2f2f]' : 'bg-gray-100';
  const borderColor = isDarkMode ? 'border-[#3d3d3d]' : 'border-gray-200';
  const textColor = isDarkMode ? 'text-[#ececec]' : 'text-gray-900';
  const secondaryText = isDarkMode ? 'text-[#b4b4b4]' : 'text-gray-600';
  const hoverBg = isDarkMode ? 'hover:bg-[#2f2f2f]' : 'hover:bg-gray-100';
  const hoverText = isDarkMode ? 'hover:text-[#ececec]' : 'hover:text-gray-900';
  const inputBg = isDarkMode ? 'bg-[#2f2f2f]' : 'bg-white';
  const menuBg = isDarkMode ? 'bg-[#2f2f2f]' : 'bg-white';
  const resizerHover = isDarkMode ? 'hover:bg-blue-600' : 'hover:bg-blue-500';

  return (
    <div className={`min-h-screen ${bgColor} font-['system-ui',-apple-system,'Segoe_UI',sans-serif] transition-colors`}>
      {/* Header */}
      <header className={`${secondaryBg} border-b ${borderColor} px-4 py-2.5 transition-colors`}>
        <div className="flex items-center justify-between max-w-[2000px] mx-auto">
          <div className="flex items-center gap-3">
            <button 
              className={`p-2 rounded-lg ${hoverBg}`}
              aria-label="Menu"
            >
              <svg className={`w-6 h-6 ${textColor}`} fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
              </svg>
            </button>

            <button className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${hoverBg} ${textColor}`}>
              <span className="text-sm font-medium">GeoNLI</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={toggleDarkMode}
              className={`p-2 rounded-lg ${hoverBg} transition-colors`}
              title={isDarkMode ? 'Light mode' : 'Dark mode'}
              aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
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

            <button className={`flex items-center gap-2 px-3 py-2 rounded-lg ${hoverBg} ${textColor}`}>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              <span className="text-sm">Share</span>
            </button>

            <button className={`flex items-center gap-2 px-3 py-2 rounded-lg ${hoverBg} ${textColor}`}>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
              <span className="text-sm">Add people</span>
            </button>

            <button
              onClick={() => navigate('/profile')}
              className={`p-2 rounded-lg ${hoverBg}`}
              title="Profile"
              aria-label="Go to profile"
            >
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-xs font-semibold">
                {authUser?.fullName?.charAt(0)?.toUpperCase() || 'U'}
              </div>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-53px)] relative">
        {/* Left Sidebar */}
        <aside
          className={`${secondaryBg} border-r ${borderColor} flex flex-col transition-all duration-300 flex-shrink-0`}
          style={{ width: sidebarCollapsed ? '64px' : `${leftWidth}px` }}
        >
          {!sidebarCollapsed ? (
            <>
              <div className="p-2 space-y-1">
                <button
                  onClick={() => setSidebarCollapsed(true)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg ${hoverBg} ${textColor}`}
                  aria-label="Close sidebar"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                  <span className="text-sm font-medium">Close sidebar</span>
                </button>

                <button
                  onClick={handleCreateNewSession}
                  disabled={isCreating}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg ${hoverBg} ${textColor} disabled:opacity-50 disabled:cursor-not-allowed`}
                  aria-label="Create new chat"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                  <span className="text-sm">{isCreating ? 'Creating...' : 'New chat'}</span>
                </button>

                <button
                  onClick={toggleSearch}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg ${hoverBg} ${textColor}`}
                  aria-label="Search chats"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span className="text-sm">Search chats</span>
                </button>

                {showSearch && (
                  <div className="px-2 py-1">
                    <input
                      ref={searchInputRef}
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search..."
                      className={`w-full px-3 py-2 ${inputBg} ${textColor} border ${borderColor} rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      aria-label="Search sessions"
                    />
                  </div>
                )}
              </div>

              <div className="px-2 py-2 border-b border-gray-800">
                <button className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg ${hoverBg} ${textColor} text-sm`}>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  <span>Library</span>
                </button>
              </div>

              <div className="flex-1 overflow-y-auto">
                <div className="px-3 py-2">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className={`text-xs font-semibold ${secondaryText} uppercase tracking-wider`}>
                      {showArchived ? 'Archived' : 'Recent'}
                    </h3>
                    <button
                      onClick={toggleArchived}
                      className={`text-xs ${secondaryText} ${hoverText}`}
                      aria-label={showArchived ? 'Show active sessions' : 'Show archived sessions'}
                    >
                      {showArchived ? 'Show active' : 'Show archived'}
                    </button>
                  </div>
                </div>

                <div className="px-2 space-y-1">
                  {filteredSessions.length === 0 ? (
                    <div className={`text-center py-8 ${secondaryText} text-sm`}>
                      {searchQuery ? 'No sessions found' : showArchived ? 'No archived sessions' : 'No sessions yet'}
                    </div>
                  ) : (
                    filteredSessions.map((session) => {
                      // FIXED: Capture session ID in local variable
                      const sessionId = session._id || session.id;  
                      
                      if (!sessionId) {
                        console.error('Session missing ID:', session);
                        return null;
                      }

                      return (
                        <div key={sessionId} className="relative group">
                          <button
                            onClick={() => setActiveSession(sessionId)}
                            className={`w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center justify-between ${
                              activeSession === sessionId
                                ? isDarkMode ? 'bg-[#2f2f2f] text-white' : 'bg-gray-200 text-gray-900'
                                : `${textColor} ${hoverBg}`
                            }`}
                            aria-label={`Select session: ${session.name}`}
                            aria-current={activeSession === sessionId ? 'true' : 'false'}
                          >
                            <div className="flex-1 min-w-0">
                              <div className="text-sm truncate">{session.name}</div>
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setShowSessionMenu(showSessionMenu === sessionId ? null : sessionId);
                              }}
                              className={`p-1 rounded ${hoverBg} opacity-0 group-hover:opacity-100 transition-opacity`}
                              aria-label="Session options"
                              aria-expanded={showSessionMenu === sessionId}
                            >
                              <svg className={`w-4 h-4 ${secondaryText}`} fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
                              </svg>
                            </button>
                          </button>

                          {showSessionMenu === sessionId && (
                            <div 
                              className={`absolute right-2 top-10 ${menuBg} border ${borderColor} rounded-lg shadow-2xl z-50 py-1 min-w-[200px]`}
                              role="menu"
                              aria-label="Session menu"
                            >
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleShareSession(sessionId);
                                }}
                                className={`w-full text-left px-4 py-2 text-sm ${textColor} ${hoverBg} flex items-center gap-3`}
                                role="menuitem"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                                </svg>
                                Share
                              </button>

                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRenameSession(sessionId);
                                }}
                                className={`w-full text-left px-4 py-2 text-sm ${textColor} ${hoverBg} flex items-center gap-3`}
                                role="menuitem"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                                Rename
                              </button>

                              <div className="relative">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setShowMoveMenu(showMoveMenu === sessionId ? null : sessionId);
                                  }}
                                  className={`w-full text-left px-4 py-2 text-sm ${textColor} ${hoverBg} flex items-center justify-between`}
                                  role="menuitem"
                                  aria-expanded={showMoveMenu === sessionId}
                                >
                                  <div className="flex items-center gap-3">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                                    </svg>
                                    Move to project
                                  </div>
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                  </svg>
                                </button>

                                {showMoveMenu === sessionId && (
                                  <div 
                                    className={`absolute left-full top-0 ml-1 ${menuBg} border ${borderColor} rounded-lg shadow-2xl py-1 min-w-[180px]`}
                                    role="menu"
                                  >
                                    {projects.length === 0 ? (
                                      <div className={`px-4 py-2 text-sm ${secondaryText}`}>
                                        No projects available
                                      </div>
                                    ) : (
                                      projects.map((project) => (
                                        <button
                                          key={project._id}
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            handleMoveToProject(sessionId, project._id);
                                          }}
                                          className={`w-full text-left px-4 py-2 text-sm ${textColor} ${hoverBg}`}
                                          role="menuitem"
                                        >
                                          {project.name}
                                        </button>
                                      ))
                                    )}
                                  </div>
                                )}
                              </div>

                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleArchiveSession(sessionId);
                                }}
                                className={`w-full text-left px-4 py-2 text-sm ${textColor} ${hoverBg} flex items-center gap-3`}
                                role="menuitem"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                                </svg>
                                {session.archived ? 'Unarchive' : 'Archive'}
                              </button>

                              <div className={`border-t ${borderColor} my-1`}></div>

                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteSession(sessionId);
                                }}
                                className={`w-full text-left px-4 py-2 text-sm text-red-500 ${hoverBg} flex items-center gap-3`}
                                role="menuitem"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                                Delete
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              <div className={`p-3 border-t ${borderColor}`}>
                <div className={`flex items-center gap-3 px-3 py-2`}>
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-sm font-semibold">
                    {authUser?.fullName?.charAt(0)?.toUpperCase() || 'U'}
                  </div>

                  <div className="flex-1 text-left">
                    <div className={`text-sm font-medium ${textColor}`}>
                      {authUser?.fullName || 'User'}
                    </div>
                    <div className={`text-xs ${secondaryText}`}>Free</div>
                  </div>

                  <button
                    onClick={handleLogout}
                    className={`p-2 rounded-lg ${hoverBg}`}
                    title="Logout"
                    aria-label="Logout"
                  >
                    <svg className={`w-4 h-4 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="p-2 space-y-2">
              <button
                onClick={() => setSidebarCollapsed(false)}
                className={`w-full p-3 rounded-lg ${hoverBg}`}
                title="Open sidebar"
                aria-label="Open sidebar"
              >
                <svg className={`w-5 h-5 ${textColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <button
                onClick={handleCreateNewSession}
                disabled={isCreating}
                className={`w-full p-3 rounded-lg ${hoverBg} disabled:opacity-50`}
                title="New chat"
                aria-label="Create new chat"
              >
                <svg className={`w-5 h-5 ${textColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
            </div>
          )}
        </aside>

        {/* Left Resizer */}
        {!sidebarCollapsed && (
          <div
            className={`w-1 ${borderColor} ${resizerHover} cursor-col-resize flex-shrink-0 group relative`}
            onMouseDown={() => setIsResizingLeft(true)}
            role="separator"
            aria-label="Resize left sidebar"
          >
            <div className="absolute inset-0 w-3 -left-1" />
          </div>
        )}

        {/* Center - Image Display */}
        <main className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 p-4 overflow-auto">
            <div className="max-w-5xl mx-auto">
              <div className="mb-4">
                <div className="flex items-center justify-between mb-3">
                  <h2 className={`text-lg font-semibold ${textColor}`}>
                    Image Workspace
                  </h2>
                  {selectedImage && (
                    <div className="flex items-center gap-1">
                      <button
                        onClick={zoomOut}
                        className={`p-2 rounded-lg ${hoverBg}`}
                        title="Zoom out"
                        aria-label="Zoom out"
                      >
                        <svg className={`w-4 h-4 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                        </svg>
                      </button>
                      <span className={`text-xs ${secondaryText} px-2`} aria-label={`Zoom level: ${imageZoom}%`}>
                        {imageZoom}%
                      </span>
                      <button
                        onClick={zoomIn}
                        className={`p-2 rounded-lg ${hoverBg}`}
                        title="Zoom in"
                        aria-label="Zoom in"
                      >
                        <svg className={`w-4 h-4 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                        </svg>
                      </button>
                      <button
                        onClick={downloadImage}
                        className={`p-2 rounded-lg ${hoverBg}`}
                        title="Download"
                        aria-label="Download image"
                      >
                        <svg className={`w-4 h-4 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                      </button>
                      <button
                        onClick={removeImage}
                        className={`p-2 rounded-lg ${hoverBg}`}
                        title="Remove"
                        aria-label="Remove image"
                      >
                        <svg className={`w-4 h-4 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div
                ref={dropZoneRef}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`${tertiaryBg} border-2 ${
                  dragActive 
                    ? (isDarkMode ? 'border-white' : 'border-black') 
                    : borderColor
                } rounded-xl transition-all ${
                  selectedImage ? 'h-[calc(100vh-240px)]' : 'h-[calc(100vh-180px)]'
                } flex items-center justify-center overflow-auto`}
                role="region"
                aria-label="Image workspace"
              >
                {selectedImage ? (
                  <img
                    src={selectedImage}
                    alt="Uploaded satellite imagery"
                    style={{ transform: `scale(${imageZoom / 100})` }}
                    className="max-w-full max-h-full object-contain transition-transform"
                  />
                ) : (
                  <div className="text-center p-12">
                    <div className={`w-20 h-20 ${isDarkMode ? 'bg-[#3d3d3d]' : 'bg-gray-200'} rounded-2xl mx-auto mb-6 flex items-center justify-center`}>
                      <svg className={`w-10 h-10 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <p className={`${textColor} mb-2 font-medium text-lg`}>
                      Drop your satellite image here
                    </p>
                    <p className={`text-sm ${secondaryText} mb-8 max-w-md mx-auto`}>
                      Supports JPEG and PNG • Best results with high-resolution imagery
                    </p>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isUploading}
                      className={`px-5 py-2.5 ${
                        isDarkMode 
                          ? 'bg-white text-black hover:bg-gray-200' 
                          : 'bg-black text-white hover:bg-gray-800'
                      } rounded-lg transition-colors font-medium text-sm inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      {isUploading ? 'Uploading...' : 'Upload Image'}
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/jpeg,image/png"
                      onChange={handleFileSelect}
                      className="hidden"
                      aria-label="Upload image file"
                    />
                  </div>
                )}
              </div>

              {selectedImage && (
                <div className={`mt-4 p-4 ${tertiaryBg} border ${borderColor} rounded-xl flex items-center justify-between`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 ${isDarkMode ? 'bg-[#4d4d4d]' : 'bg-gray-200'} rounded-lg flex items-center justify-center`}>
                      <svg className={`w-5 h-5 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <p className={`text-sm ${textColor} font-medium`}>{fileName}</p>
                      <p className={`text-xs ${secondaryText} mt-0.5`}>Ready for analysis</p>
                    </div>
                  </div>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className={`px-4 py-2 text-sm ${secondaryText} ${hoverText} ${hoverBg} rounded-lg`}
                    aria-label="Change image"
                  >
                    Change
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png"
                    onChange={handleFileSelect}
                    className="hidden"
                    aria-label="Upload new image file"
                  />
                </div>
              )}
            </div>
          </div>
        </main>

        {/* Right Resizer */}
        <div
          className={`w-1 ${borderColor} ${resizerHover} cursor-col-resize flex-shrink-0 group relative`}
          onMouseDown={() => setIsResizingRight(true)}
          role="separator"
          aria-label="Resize right sidebar"
        >
          <div className="absolute inset-0 w-3 -left-1" />
        </div>

        {/* Right Sidebar - Chat */}
        <aside
          className={`${secondaryBg} border-l ${borderColor} flex flex-col flex-shrink-0`}
          style={{ width: `${rightWidth}px` }}
        >
          <div className={`p-4 border-b ${borderColor}`}>
            <h2 className={`text-base font-semibold ${textColor} mb-1`}>
              Analysis Console
            </h2>
            <p className={`text-xs ${secondaryText}`}>
              AI-powered geospatial analysis
            </p>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className={`${tertiaryBg} rounded-xl p-5`}>
                <h3 className={`font-semibold ${textColor} mb-3 text-sm`}>
                  Getting Started
                </h3>
                <div className={`text-sm ${secondaryText} space-y-2.5 leading-relaxed`}>
                  <p>Upload an image and ask me to:</p>
                  <ul className="space-y-2 ml-1" role="list">
                    <li className="flex items-start gap-2">
                      <span className={isDarkMode ? 'text-gray-600' : 'text-gray-400'} aria-hidden="true">•</span>
                      <span>Identify geographical features</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className={isDarkMode ? 'text-gray-600' : 'text-gray-400'} aria-hidden="true">•</span>
                      <span>Compare different regions</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className={isDarkMode ? 'text-gray-600' : 'text-gray-400'} aria-hidden="true">•</span>
                      <span>Detect land cover patterns</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className={isDarkMode ? 'text-gray-600' : 'text-gray-400'} aria-hidden="true">•</span>
                      <span>Summarize the scene</span>
                    </li>
                  </ul>
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <div key={msg._id} className="group">
                    <div className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div 
                        className={`max-w-[85%] ${
                          msg.sender === 'user'
                            ? isDarkMode ? 'bg-white text-black' : 'bg-black text-white'
                            : tertiaryBg
                        } rounded-2xl px-4 py-3`}
                        role="article"
                        aria-label={`${msg.sender === 'user' ? 'Your' : 'AI'} message`}
                      >
                        <p className={`text-sm leading-relaxed ${msg.sender === 'ai' ? textColor : ''}`}>
                          {msg.text}
                        </p>
                        <div className="flex items-center justify-between mt-2 gap-2">
                          <span className={`text-xs ${msg.sender === 'user' ? (isDarkMode ? 'text-gray-600' : 'text-gray-300') : secondaryText}`}>
                            {new Date(msg.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                          <button
                            onClick={() => copyMessage(msg.text)}
                            className="opacity-0 group-hover:opacity-100 transition-opacity"
                            title="Copy message"
                            aria-label="Copy message to clipboard"
                          >
                            <svg className={`w-3.5 h-3.5 ${msg.sender === 'user' ? (isDarkMode ? 'text-gray-600' : 'text-gray-300') : secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="flex justify-start" role="status" aria-label="AI is typing">
                    <div className={`${tertiaryBg} rounded-2xl px-4 py-3`}>
                      <div className="flex items-center gap-1">
                        <div className={`w-2 h-2 ${isDarkMode ? 'bg-gray-500' : 'bg-gray-400'} rounded-full animate-pulse`}></div>
                        <div className={`w-2 h-2 ${isDarkMode ? 'bg-gray-500' : 'bg-gray-400'} rounded-full animate-pulse`} style={{ animationDelay: '0.2s' }}></div>
                        <div className={`w-2 h-2 ${isDarkMode ? 'bg-gray-500' : 'bg-gray-400'} rounded-full animate-pulse`} style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </>
            )}
          </div>

          <div className={`p-4 border-t ${borderColor}`}>
            <div className={`${inputBg} border ${borderColor} rounded-2xl p-3 focus-within:border-gray-500`}>
              <textarea
                value={chatMessage}
                onChange={handleChatMessageChange}
                onKeyPress={handleKeyPress}
                placeholder="Ask anything..."
                rows={2}
                disabled={isSending}
                className={`w-full ${inputBg} ${textColor} placeholder-${secondaryText.replace('text-', '')} text-sm focus:outline-none resize-none disabled:opacity-50 disabled:cursor-not-allowed`}
                aria-label="Message input"
              />
              <div className="flex items-center justify-between mt-2">
                <div className="flex items-center gap-1">
                  <button
                    onClick={handleExportChat}
                    disabled={messages.length === 0}
                    className={`p-1.5 rounded-lg ${hoverBg} disabled:opacity-50 disabled:cursor-not-allowed`}
                    title="Export chat"
                    aria-label="Export chat history"
                  >
                    <svg className={`w-4 h-4 ${secondaryText}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </button>
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!chatMessage.trim() || isSending}
                  className={`p-2 rounded-lg ${
                    isDarkMode 
                      ? 'bg-white text-black hover:bg-gray-200' 
                      : 'bg-black text-white hover:bg-gray-800'
                  } disabled:opacity-50 disabled:cursor-not-allowed transition-colors`}
                  aria-label="Send message"
                >
                  {isSending ? (
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}