import axios from "axios";

const request = axios.create({
  baseURL: "http://127.0.0.1:5000",
  timeout: 5000,
});

request.interceptors.request.use((config) => {
  const myToken = localStorage.getItem("token");
  if (myToken) {
    config.headers.Authorization = "Bearer " + myToken;
  }
  return config;
});

export default request;
