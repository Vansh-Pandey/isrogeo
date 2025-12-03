import { create } from "zustand";
import { axiosInstance } from "../libs/axios";
import { toast } from "react-toastify";

export const useMessageStore = create((set, get) => ({
  messages: [],
  isLoading: false,
  isSending: false,
  isTyping: false,

  // Fetch messages for a session
  fetchMessages: async (sessionId) => {
    if (!sessionId) {
      set({ messages: [] });
      return;
    }

    set({ isLoading: true });
    try {
      const res = await axiosInstance.get(`/messages/${sessionId}`);
      set({ messages: res.data });
    } catch (error) {
      console.error("Error fetching messages:", error);
      toast.error("Failed to load messages");
      set({ messages: [] });
    } finally {
      set({ isLoading: false });
    }
  },

  // Send a message
  sendMessage: async (sessionId, messageText, imageData = null) => {
    if (!messageText.trim() && !imageData) return null;

    set({ isSending: true });

    const tempMessage = {
      _id: `temp-${Date.now()}`,
      sessionId,
      text: messageText,
      sender: "user",
      imageData,
      timestamp: new Date().toISOString(),
      createdAt: new Date().toISOString(),
    };

    // Optimistically add user message
    set((state) => ({
      messages: [...state.messages, tempMessage],
    }));

    try {
      // Send message to backend
      const res = await axiosInstance.post("/messages", {
        sessionId,
        text: messageText,
        imageData,
      });

      // Replace temp message with real message
      set((state) => ({
        messages: state.messages.map((m) =>
          m._id === tempMessage._id ? res.data : m
        ),
      }));

      // Start AI typing indicator
      set({ isTyping: true });

      // Get AI response
      const aiRes = await axiosInstance.post("/messages/ai-response", {
        sessionId,
        messageId: res.data._id,
      });

      // Add AI response
      set((state) => ({
        messages: [...state.messages, aiRes.data],
        isTyping: false,
      }));

      return aiRes.data;
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to send message");

      // Remove temp message on error
      set((state) => ({
        messages: state.messages.filter((m) => m._id !== tempMessage._id),
        isTyping: false,
      }));

      return null;
    } finally {
      set({ isSending: false });
    }
  },

  // Delete a message
  deleteMessage: async (messageId) => {
    try {
      await axiosInstance.delete(`/messages/${messageId}`);
      set((state) => ({
        messages: state.messages.filter((m) => m._id !== messageId),
      }));
      toast.success("Message deleted", { autoClose: 1000 });
    } catch (error) {
      console.error("Error deleting message:", error);
      toast.error("Failed to delete message");
    }
  },

  // Clear messages for current session
  clearMessages: () => {
    set({ messages: [] });
  },

  // Export chat
  exportChat: (sessionName) => {
    const messages = get().messages;
    const chatText = messages
      .map((m) => {
        const time = new Date(m.createdAt).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });
        const sender = m.sender === "user" ? "You" : "AI";
        return `[${time}] ${sender}: ${m.text}`;
      })
      .join("\n");

    const blob = new Blob([chatText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${sessionName || "chat"}-export.txt`;
    link.click();
    URL.revokeObjectURL(url);

    toast.success("Chat exported", { autoClose: 1000 });
  },

  // Copy message to clipboard
  copyMessage: (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard", { autoClose: 1000 });
  },
}));