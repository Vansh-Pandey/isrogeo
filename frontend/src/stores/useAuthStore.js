import { axiosInstance } from "../libs/axios";
import { create } from "zustand";
import { toast } from "react-toastify";

export const useAuthStore = create((set) => ({
  authUser: null,
  isRegistering: false,
  isLogging: false,
  isUpdatingProfile: false,
  isCheckingAuth: true,

  // Check authentication
  checkAuth: async () => {
    try {
      const res = await axiosInstance.get("/auth/check");
      set({ authUser: res.data });
    } catch (error) {
      console.log("Error in checkAuth:", error);
      set({ authUser: null });
    } finally {
      set({ isCheckingAuth: false });
    }
  },

  // Signup
  signup: async (data) => {
    set({ isRegistering: true });
    try {
      const res = await axiosInstance.post("/auth/signup", data);
      set({ authUser: res.data });
      toast.success("Account created successfully", { autoClose: 1000 });
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || "Signup failed", {
        autoClose: 1000,
      });
      return false;
    } finally {
      set({ isRegistering: false });
    }
  },

  // Login
  login: async (userData) => {
    set({ isLogging: true });
    try {
      const res = await axiosInstance.post("/auth/login", userData);
      set({ authUser: res.data });
      toast.success("Logged in successfully", { autoClose: 1000 });
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return true;
    } catch (error) {
      console.error("Login Error:", error.response?.data?.message || error.message);
      toast.error(error.response?.data?.message || "Login failed", {
        autoClose: 1000,
      });
      return false;
    } finally {
      set({ isLogging: false });
    }
  },

  // Logout
  logout: async () => {
    try {
      await axiosInstance.post("/auth/logout");
      set({ authUser: null });
      toast.success("Logged out successfully", { autoClose: 1000 });
      return true;
    } catch (error) {
      console.error("Logout Error:", error.response?.data?.message || error.message);
      toast.error(error.response?.data?.message || "Logout failed", {
        autoClose: 1000,
      });
      return false;
    }
  },

  // Update profile
  updateProfile: async (updates) => {
    set({ isUpdatingProfile: true });
    try {
      const res = await axiosInstance.put("/auth/update-profile", updates);
      set({ authUser: res.data });
      toast.success("Profile updated successfully", { autoClose: 1000 });
      return res.data;
    } catch (error) {
      console.error("Update Profile Error:", error.response?.data?.message || error.message);
      toast.error(error.response?.data?.message || "Failed to update profile", {
        autoClose: 1000,
      });
      return null;
    } finally {
      set({ isUpdatingProfile: false });
    }
  },

  // Update profile picture
  updateProfilePicture: async (imageFile) => {
    set({ isUpdatingProfile: true });
    try {
      const formData = new FormData();
      formData.append("profilePic", imageFile);

      const res = await axiosInstance.put("/auth/update-profile-picture", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      set({ authUser: res.data });
      toast.success("Profile picture updated", { autoClose: 1000 });
      return res.data;
    } catch (error) {
      console.error("Update Profile Picture Error:", error.response?.data?.message || error.message);
      toast.error(error.response?.data?.message || "Failed to update profile picture", {
        autoClose: 1000,
      });
      return null;
    } finally {
      set({ isUpdatingProfile: false });
    }
  },

  // Change password
  changePassword: async (currentPassword, newPassword) => {
    try {
      await axiosInstance.put("/auth/change-password", {
        currentPassword,
        newPassword,
      });
      toast.success("Password changed successfully", { autoClose: 1000 });
      return true;
    } catch (error) {
      console.error("Change Password Error:", error.response?.data?.message || error.message);
      toast.error(error.response?.data?.message || "Failed to change password", {
        autoClose: 1000,
      });
      return false;
    }
  },

  // Delete account
  deleteAccount: async (password) => {
    try {
      await axiosInstance.delete("/auth/delete-account", {
        data: { password },
      });
      set({ authUser: null });
      toast.success("Account deleted successfully", { autoClose: 1000 });
      return true;
    } catch (error) {
      console.error("Delete Account Error:", error.response?.data?.message || error.message);
      toast.error(error.response?.data?.message || "Failed to delete account", {
        autoClose: 1000,
      });
      return false;
    }
  },
}));