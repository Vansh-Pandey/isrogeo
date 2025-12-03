import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useUIStore = create(
  persist(
    (set, get) => ({
      // Theme
      isDarkMode: true,

      // Sidebar
      sidebarCollapsed: false,
      leftWidth: 256,
      rightWidth: 380,

      // Search
      showSearch: false,
      searchQuery: "",

      // Filters
      showArchived: false,

      // Modals
      showSessionMenu: null,
      showMoveMenu: null,

      // Drag and drop
      dragActive: false,

      // Toggle dark mode
      toggleDarkMode: () => {
        set((state) => ({ isDarkMode: !state.isDarkMode }));
      },

      // Set dark mode
      setDarkMode: (isDark) => {
        set({ isDarkMode: isDark });
      },

      // Toggle sidebar
      toggleSidebar: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
      },

      // Set sidebar collapsed
      setSidebarCollapsed: (collapsed) => {
        set({ sidebarCollapsed: collapsed });
      },

      // Set left sidebar width
      setLeftWidth: (width) => {
        set({ leftWidth: Math.max(200, Math.min(500, width)) });
      },

      // Set right sidebar width
      setRightWidth: (width) => {
        set({ rightWidth: Math.max(300, Math.min(600, width)) });
      },

      // Toggle search
      toggleSearch: () => {
        set((state) => ({ 
          showSearch: !state.showSearch,
          searchQuery: state.showSearch ? "" : state.searchQuery 
        }));
      },

      // Set search query
      setSearchQuery: (query) => {
        set({ searchQuery: query });
      },

      // Clear search
      clearSearch: () => {
        set({ searchQuery: "", showSearch: false });
      },

      // Toggle archived
      toggleArchived: () => {
        set((state) => ({ showArchived: !state.showArchived }));
      },

      // Set show archived
      setShowArchived: (show) => {
        set({ showArchived: show });
      },

      // Set session menu
      setShowSessionMenu: (sessionId) => {
        set({ showSessionMenu: sessionId });
      },

      // Close session menu
      closeSessionMenu: () => {
        set({ showSessionMenu: null });
      },

      // Set move menu
      setShowMoveMenu: (sessionId) => {
        set({ showMoveMenu: sessionId });
      },

      // Close move menu
      closeMoveMenu: () => {
        set({ showMoveMenu: null });
      },

      // Close all menus
      closeAllMenus: () => {
        set({ 
          showSessionMenu: null, 
          showMoveMenu: null 
        });
      },

      // Set drag active
      setDragActive: (active) => {
        set({ dragActive: active });
      },

      // Reset UI to defaults
      resetUI: () => {
        set({
          sidebarCollapsed: false,
          leftWidth: 256,
          rightWidth: 380,
          showSearch: false,
          searchQuery: "",
          showArchived: false,
          showSessionMenu: null,
          showMoveMenu: null,
          dragActive: false,
        });
      },
    }),
    {
      name: "geonli-ui-storage",
      partialize: (state) => ({
        isDarkMode: state.isDarkMode,
        leftWidth: state.leftWidth,
        rightWidth: state.rightWidth,
      }),
    }
  )
);