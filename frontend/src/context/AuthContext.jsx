import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const DEMO_USERS = [
  {
    role: "SECRETARY",
    title: "Principal Secretary (IAS)",
    name: "Shri M. K. Das, IAS",
    department: "Roads & Buildings Department, Govt. of Gujarat",
    email: "secretary@rnb.gujarat.gov.in",
    password: "secretary123",
  },
  {
    role: "ADMIN",
    title: "Chief Engineer (Admin)",
    name: "Shri Rajesh Patel",
    department: "State Headquarters, Gandhinagar",
    email: "admin@rnb.gujarat.gov.in",
    password: "admin123",
  },
  {
    role: "ENGINEER",
    title: "Executive Engineer",
    name: "Er. Amit Shah",
    department: "Ahmedabad Division",
    email: "engineer@rnb.gujarat.gov.in",
    password: "engineer123",
  },
  {
    role: "INSPECTOR",
    title: "QC Field Assistant Engineer",
    name: "Smt. Priya Desai",
    department: "Quality Control Division, Vadodara",
    email: "inspector@rnb.gujarat.gov.in",
    password: "inspector123",
  },
  {
    role: "CONTRACTOR",
    title: "EPC Concessionaire Partner",
    name: "M/s L&T Infrastructure",
    department: "Special Projects Division",
    email: "contractor@rnb.gujarat.gov.in",
    password: "contractor123",
  },
];

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem("rnb_user");
    const token = localStorage.getItem("rnb_token");
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem("rnb_user");
        localStorage.removeItem("rnb_token");
      }
    }
    setLoading(false);
  }, []);

  const loginDemoUser = async (demoUser) => {
    try {
      const res = await api.login(demoUser.email, demoUser.password);
      setUser(res.user);
      return res.user;
    } catch (err) {
      // Graceful fallback for demo presentation
      const fallbackUser = {
        username: demoUser.email,
        email: demoUser.email,
        full_name: demoUser.name,
        role: demoUser.role,
        department: demoUser.department,
        designation: demoUser.title,
      };
      localStorage.setItem("rnb_user", JSON.stringify(fallbackUser));
      localStorage.setItem("rnb_token", "demo-token-" + demoUser.role);
      setUser(fallbackUser);
      return fallbackUser;
    }
  };

  const login = async (username, password) => {
    const res = await api.login(username, password);
    setUser(res.user);
    return res.user;
  };

  const register = async (userData) => {
    await api.register(userData);
    return await login(userData.username, userData.password);
  };

  const logout = () => {
    api.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, loginDemoUser, DEMO_USERS }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
