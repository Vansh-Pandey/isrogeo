import { create } from "zustand";
import { axiosInstance } from "../libs/axios";
import { toast } from "react-toastify";

export const useImageStore = create((set, get) => ({
  selectedImage: null,
  fileName: "",
  imageZoom: 100,
  isUploading: false,
  uploadProgress: 0,

  // Upload image
  uploadImage: async (file, sessionId) => {
    if (!file || (!file.type.includes("image/jpeg") && !file.type.includes("image/png"))) {
      toast.error("Please upload a JPEG or PNG image");
      return null;
    }

    set({ isUploading: true, uploadProgress: 0 });

    try {
      // Convert file to base64
      const base64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      // Upload to backend
      const formData = new FormData();
      formData.append("image", file);
      formData.append("sessionId", sessionId);

      const res = await axiosInstance.post("/images/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          set({ uploadProgress: progress });
        },
      });

      set({
        selectedImage: base64,
        fileName: file.name,
        uploadProgress: 100,
      });

      toast.success("Image uploaded", { autoClose: 1000 });
      return res.data;
    } catch (error) {
      console.error("Error uploading image:", error);
      toast.error("Failed to upload image");
      return null;
    } finally {
      set({ isUploading: false });
      setTimeout(() => set({ uploadProgress: 0 }), 1000);
    }
  },

  // Set image from file (local preview)
  setImageFromFile: (file) => {
    if (!file || (!file.type.includes("image/jpeg") && !file.type.includes("image/png"))) {
      toast.error("Please upload a JPEG or PNG image");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      set({
        selectedImage: e.target.result,
        fileName: file.name,
      });
    };
    reader.readAsDataURL(file);
  },

  // Remove image
  removeImage: async (imageId) => {
    try {
      if (imageId) {
        await axiosInstance.delete(`/images/${imageId}`);
      }
      set({
        selectedImage: null,
        fileName: "",
        imageZoom: 100,
      });
      toast.success("Image removed", { autoClose: 1000 });
    } catch (error) {
      console.error("Error removing image:", error);
      toast.error("Failed to remove image");
    }
  },

  // Download image
  downloadImage: () => {
    const { selectedImage, fileName } = get();
    if (!selectedImage) return;

    const link = document.createElement("a");
    link.href = selectedImage;
    link.download = fileName || "satellite-image.png";
    link.click();

    toast.success("Image downloaded", { autoClose: 1000 });
  },

  // Set zoom level
  setImageZoom: (zoom) => {
    set({ imageZoom: Math.max(50, Math.min(200, zoom)) });
  },

  // Zoom in
  zoomIn: () => {
    set((state) => ({
      imageZoom: Math.min(200, state.imageZoom + 25),
    }));
  },

  // Zoom out
  zoomOut: () => {
    set((state) => ({
      imageZoom: Math.max(50, state.imageZoom - 25),
    }));
  },

  // Reset zoom
  resetZoom: () => {
    set({ imageZoom: 100 });
  },

  // Analyze image with AI
  analyzeImage: async (sessionId, prompt) => {
    const { selectedImage } = get();
    if (!selectedImage) {
      toast.error("Please upload an image first");
      return null;
    }

    try {
      const res = await axiosInstance.post("/images/analyze", {
        sessionId,
        imageData: selectedImage,
        prompt,
      });

      toast.success("Analysis complete", { autoClose: 1000 });
      return res.data;
    } catch (error) {
      console.error("Error analyzing image:", error);
      toast.error("Failed to analyze image");
      return null;
    }
  },

  // Clear image data
  clearImage: () => {
    set({
      selectedImage: null,
      fileName: "",
      imageZoom: 100,
    });
  },
}));