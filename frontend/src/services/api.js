import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to get active user ID from localStorage
export const getActiveUserId = () => {
  const userJson = localStorage.getItem('user');
  if (userJson) {
    try {
      const user = JSON.parse(userJson);
      return user.id;
    } catch (e) {
      return null;
    }
  }
  return null;
};

// Auth APIs
export const loginUser = async (email, password) => {
  const res = await api.post('/auth/login', { email, password });
  return res.data;
};

export const registerUser = async (userData) => {
  const res = await api.post('/auth/register', userData);
  return res.data;
};

// Course APIs
export const fetchCourses = async () => {
  const res = await api.get('/courses');
  return res.data;
};

export const fetchCourseDetails = async (courseId) => {
  const userId = getActiveUserId();
  const res = await api.get(`/courses/${courseId}`, {
    params: { user_id: userId }
  });
  return res.data;
};

export const searchCourses = async (queryStr, filters = {}) => {
  const userId = getActiveUserId();
  const res = await api.get('/courses/search', {
    params: { q: queryStr, ...filters, user_id: userId }
  });
  return res.data;
};

// Recommendation APIs
export const fetchRecommendations = async (userId) => {
  const uid = userId || getActiveUserId() || 'u-demo-cse';
  const res = await api.get(`/recommendations/${uid}`);
  return res.data;
};

export const fetchTrendingCourses = async () => {
  const res = await api.get('/recommendations/trending');
  return res.data;
};

export const fetchContextualRecommendations = async (query, userId) => {
  const uid = userId || getActiveUserId();
  const res = await api.get('/recommendations/contextual', {
    params: { q: query, user_id: uid }
  });
  return res.data;
};

export const fetchDepartmentCourses = async (department) => {
  const res = await api.get(`/recommendations/department/${department}`);
  return res.data;
};

// Interaction APIs
export const recordInteraction = async (eventType, courseId = null, metadata = {}) => {
  const userId = getActiveUserId();
  if (!userId) return;
  try {
    await api.post('/interactions', {
      user_id: userId,
      event_type: eventType,
      course_id: courseId,
      metadata
    });
  } catch (e) {
    console.error('Failed to log interaction:', e);
  }
};

export const toggleWishlist = async (courseId) => {
  const userId = getActiveUserId();
  if (!userId) return { wishlisted: false };
  const res = await api.post('/interactions/wishlist', { user_id: userId, course_id: courseId });
  return res.data;
};

export const enrollCourse = async (courseId) => {
  const userId = getActiveUserId();
  if (!userId) return { enrolled: false };
  const res = await api.post('/interactions/enrollment', { user_id: userId, course_id: courseId });
  return res.data;
};

export const markCourseCompleted = async (courseId) => {
  const userId = getActiveUserId();
  if (!userId) return { completed: false };
  const res = await api.post('/interactions/completion', { user_id: userId, course_id: courseId });
  return res.data;
};

// User Profile & History
export const fetchUserProfile = async (userId) => {
  const uid = userId || getActiveUserId();
  if (!uid) return null;
  const res = await api.get(`/user/${uid}`);
  return res.data.user;
};

export const fetchUserInterests = async (userId) => {
  const uid = userId || getActiveUserId();
  if (!uid) return [];
  const res = await api.get(`/user/${uid}/interests`);
  return res.data.interests;
};

export const fetchUserWishlist = async (userId) => {
  const uid = userId || getActiveUserId();
  if (!uid) return [];
  const res = await api.get(`/user/${uid}/wishlist`);
  return res.data.wishlist;
};

export const fetchUserEnrollments = async (userId) => {
  const uid = userId || getActiveUserId();
  if (!uid) return [];
  const res = await api.get(`/user/${uid}/enrollments`);
  return res.data.enrollments;
};

export const fetchLearningPath = async (userId, role) => {
  const uid = userId || getActiveUserId() || 'u-demo-cse';
  const res = await api.get(`/user/learning-path/${uid}`, {
    params: { role }
  });
  return res.data;
};

// Knowledge Graph
export const fetchKnowledgeGraphData = async (userId) => {
  const uid = userId || getActiveUserId() || 'u-demo-cse';
  const res = await api.get(`/knowledge-graph/${uid}`);
  return res.data;
};

// AI Assistant Chat
export const sendChatMessage = async (message) => {
  const userId = getActiveUserId();
  const res = await api.post('/chat', { user_id: userId, message });
  return res.data;
};

export default api;
