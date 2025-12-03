import { create } from "zustand";
import { axiosInstance } from "../libs/axios";
import { toast } from "react-toastify";

export const useProjectStore = create((set, get) => ({
  projects: [],
  activeProject: null,
  isLoading: false,
  isCreating: false,
  isUpdating: false,
  isDeleting: false,

  // Fetch all projects
  fetchProjects: async () => {
    set({ isLoading: true });
    try {
      const res = await axiosInstance.get("/projects");
      set({ projects: res.data });
    } catch (error) {
      console.error("Error fetching projects:", error);
      toast.error("Failed to load projects");
    } finally {
      set({ isLoading: false });
    }
  },

  // Create new project
  createProject: async (projectData) => {
    set({ isCreating: true });
    try {
      const res = await axiosInstance.post("/projects", {
        name: projectData.name || `Project ${get().projects.length + 1}`,
        description: projectData.description || "",
        color: projectData.color || "#6366f1",
      });

      set((state) => ({
        projects: [...state.projects, res.data],
      }));

      toast.success("Project created", { autoClose: 1000 });
      return res.data;
    } catch (error) {
      console.error("Error creating project:", error);
      toast.error("Failed to create project");
      return null;
    } finally {
      set({ isCreating: false });
    }
  },

  // Update project
  updateProject: async (projectId, updates) => {
    set({ isUpdating: true });
    try {
      const res = await axiosInstance.put(`/projects/${projectId}`, updates);

      set((state) => ({
        projects: state.projects.map((p) =>
          p._id === projectId ? res.data : p
        ),
      }));

      toast.success("Project updated", { autoClose: 1000 });
      return res.data;
    } catch (error) {
      console.error("Error updating project:", error);
      toast.error("Failed to update project");
      return null;
    } finally {
      set({ isUpdating: false });
    }
  },

  // Delete project
  deleteProject: async (projectId) => {
    set({ isDeleting: true });
    try {
      await axiosInstance.delete(`/projects/${projectId}`);

      set((state) => ({
        projects: state.projects.filter((p) => p._id !== projectId),
        activeProject:
          state.activeProject === projectId ? null : state.activeProject,
      }));

      toast.success("Project deleted", { autoClose: 1000 });
      return true;
    } catch (error) {
      console.error("Error deleting project:", error);
      toast.error("Failed to delete project");
      return false;
    } finally {
      set({ isDeleting: false });
    }
  },

  // Set active project
  setActiveProject: (projectId) => {
    set({ activeProject: projectId });
  },

  // Get sessions in a project
  getProjectSessions: async (projectId) => {
    try {
      const res = await axiosInstance.get(`/projects/${projectId}/sessions`);
      return res.data;
    } catch (error) {
      console.error("Error fetching project sessions:", error);
      toast.error("Failed to load project sessions");
      return [];
    }
  },

  // Clear projects (local only)
  clearProjects: () => {
    set({ projects: [], activeProject: null });
  },
}));