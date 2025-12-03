import { create } from "zustand";
import { axiosInstance } from "../libs/axios";
import { toast } from "react-toastify";

export const useSessionStore = create((set, get) => ({
  sessions: [],
  activeSession: null,
  isLoading: false,
  isCreating: false,
  isUpdating: false,
  isDeleting: false,

  // Fetch all sessions
  fetchSessions: async () => {
    set({ isLoading: true });
    try {
      const res = await axiosInstance.get("/sessions");
      
      // DEBUG: Log the response
      console.log('🔍 Fetched sessions from API:', res.data);
      console.log('🔍 First session structure:', res.data[0]);
      
      // Ensure all sessions have _id field
      const normalizedSessions = res.data.map(session => {
        if (!session._id && session.id) {
          console.warn('⚠️ Session missing _id, using id:', session);
          return { ...session, _id: session.id };
        }
        if (!session._id) {
          console.error('❌ Session missing both _id and id:', session);
        }
        return session;
      });
      
      console.log('✅ Normalized sessions:', normalizedSessions);
      
      set({ 
        sessions: normalizedSessions,
        activeSession: normalizedSessions[0]?._id || null 
      });
    } catch (error) {
      console.error("Error fetching sessions:", error);
      toast.error("Failed to load sessions");
    } finally {
      set({ isLoading: false });
    }
  },

  // Create new session
  createSession: async (sessionData) => {
    set({ isCreating: true });
    try {
      const res = await axiosInstance.post("/sessions", {
        name: sessionData.name || `New Analysis ${get().sessions.length + 1}`,
        archived: false,
      });
      
      // DEBUG: Log created session
      console.log('🔍 Created session response:', res.data);
      console.log('🔍 Created session _id:', res.data._id);
      
      // Ensure the session has _id
      const createdSession = res.data._id ? res.data : { ...res.data, _id: res.data.id };
      
      set((state) => ({
        sessions: [createdSession, ...state.sessions],
        activeSession: createdSession._id,
      }));
      
      toast.success("Session created", { autoClose: 1000 });
      return createdSession;
    } catch (error) {
      console.error("Error creating session:", error);
      toast.error("Failed to create session");
      return null;
    } finally {
      set({ isCreating: false });
    }
  },

  // Update session
  updateSession: async (sessionId, updates) => {
    // Validation
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
      console.error('❌ Invalid session ID in updateSession:', sessionId);
      toast.error("Invalid session ID");
      return null;
    }

    set({ isUpdating: true });
    try {
      console.log('🔍 Updating session:', sessionId, 'with:', updates);
      
      const res = await axiosInstance.put(`/sessions/${sessionId}`, updates);
      
      console.log('🔍 Updated session response:', res.data);
      
      // Ensure the session has _id
      const updatedSession = res.data._id ? res.data : { ...res.data, _id: res.data.id };
      
      set((state) => ({
        sessions: state.sessions.map((s) =>
          s._id === sessionId ? updatedSession : s
        ),
      }));
      
      toast.success("Session updated", { autoClose: 1000 });
      return updatedSession;
    } catch (error) {
      console.error("Error updating session:", error);
      toast.error(error.response?.data?.detail || "Failed to update session");
      return null;
    } finally {
      set({ isUpdating: false });
    }
  },

  // Rename session
  renameSession: async (sessionId, newName) => {
    if (!sessionId || !newName) {
      console.error('❌ Invalid parameters for renameSession:', { sessionId, newName });
      return null;
    }
    return get().updateSession(sessionId, { name: newName });
  },

  // Archive session
  archiveSession: async (sessionId) => {
    if (!sessionId) {
      console.error('❌ Invalid session ID in archiveSession:', sessionId);
      return null;
    }

    const session = get().sessions.find((s) => s._id === sessionId);
    if (!session) {
      console.error('❌ Session not found:', sessionId);
      return null;
    }

    const result = await get().updateSession(sessionId, { 
      archived: !session.archived 
    });

    if (result && get().activeSession === sessionId) {
      const activeSessions = get().sessions.filter((s) => !s.archived);
      set({ activeSession: activeSessions[0]?._id || null });
    }

    return result;
  },

  // Delete session
  deleteSession: async (sessionId) => {
    // Validation
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
      console.error('❌ Invalid session ID in deleteSession:', sessionId);
      toast.error("Invalid session ID");
      return false;
    }

    console.log('🗑️ Attempting to delete session:', sessionId);

    const activeSessions = get().sessions.filter((s) => !s.archived);
    if (activeSessions.length <= 1) {
      toast.error("Cannot delete the last active session");
      return false;
    }

    set({ isDeleting: true });
    try {
      await axiosInstance.delete(`/sessions/${sessionId}`);
      
      console.log('✅ Session deleted successfully:', sessionId);
      
      set((state) => {
        const newSessions = state.sessions.filter((s) => s._id !== sessionId);
        const newActiveSession =
          state.activeSession === sessionId
            ? newSessions[0]?._id || null
            : state.activeSession;

        return {
          sessions: newSessions,
          activeSession: newActiveSession,
        };
      });
      
      toast.success("Session deleted", { autoClose: 1000 });
      return true;
    } catch (error) {
      console.error("❌ Error deleting session:", error);
      console.error("Session ID that failed:", sessionId);
      toast.error(error.response?.data?.detail || "Failed to delete session");
      return false;
    } finally {
      set({ isDeleting: false });
    }
  },

  // Set active session
  setActiveSession: (sessionId) => {
    if (!sessionId) {
      console.warn('⚠️ Attempting to set null/undefined as active session');
    }
    console.log('🔍 Setting active session:', sessionId);
    set({ activeSession: sessionId });
  },

  // Move session to project
  moveToProject: async (sessionId, projectId) => {
    if (!sessionId || !projectId) {
      console.error('❌ Invalid parameters for moveToProject:', { sessionId, projectId });
      return null;
    }
    return get().updateSession(sessionId, { projectId });
  },

  // Share session
  shareSession: async (sessionId) => {
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
      console.error('❌ Invalid session ID in shareSession:', sessionId);
      toast.error("Invalid session ID");
      return null;
    }

    try {
      console.log('🔗 Sharing session:', sessionId);
      
      const res = await axiosInstance.post(`/sessions/${sessionId}/share`);
      const shareLink = res.data.shareLink;
      
      await navigator.clipboard.writeText(shareLink);
      toast.success("Share link copied to clipboard!", { autoClose: 1000 });
      return shareLink;
    } catch (error) {
      console.error("❌ Error sharing session:", error);
      toast.error(error.response?.data?.detail || "Failed to share session");
      return null;
    }
  },

  // Clear all sessions (local only)
  clearSessions: () => {
    set({ sessions: [], activeSession: null });
  },
}));